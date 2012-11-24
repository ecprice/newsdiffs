#!/usr/bin/python

import cookielib
from datetime import datetime, timedelta
import errno
from frontend import models
import httplib
import logging
import os
import re
import socket
import sqlalchemy
import subprocess
import sys
import time
import traceback
import urllib2

import diff_match_patch

# Different versions of BeautifulSoup have different properties.
# Some work with one site, some with another.
# This is BeautifulSoup 3.2.
from BeautifulSoup import BeautifulSoup, Tag
# This is BeautifulSoup 4
import bs4

GIT_PROGRAM='git'

# This formatter is like the default but uses a period rather than a comma
# to separate the milliseconds
class MyFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return logging.Formatter.formatTime(self, record,
                                            datefmt).replace(',', '.')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = MyFormatter('%(asctime)s:%(levelname)s:%(message)s')
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
ch.setFormatter(formatter)
logger.addHandler(ch)


from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--update',
            action='store_true',
            default=False,
            help='DEPRECATED; this is the default'),
        make_option('--all',
            action='store_true',
            default=False,
            help='Update _all_ stored articles'),
        )
    help = '''Scrape websites.

By default, scan front pages for new articles, and scan
existing and new articles to archive their current contents.

Articles that haven't changed in a while are skipped if we've
scanned them recently, unless --all is passed.
'''.strip()

    def handle(self, *args, **options):
        ch = logging.FileHandler('/tmp/newsdiffs_logging', mode='w')
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        ch = logging.FileHandler('/tmp/newsdiffs_logging_errs', mode='a')
        ch.setLevel(logging.WARNING)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        cleanup_git_repo()
        update_articles()
        update_versions(options['all'])

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

# Begin utility functions

# subprocess.check_output appeared in python 2.7.
# Linerva only has 2.6
def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    from subprocess import PIPE, CalledProcessError, Popen
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        err = CalledProcessError(retcode, cmd)
        err.output = output
        raise err
    return output

if not hasattr(subprocess, 'check_output'):
    subprocess.check_output = check_output

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

# Begin hot patch for https://bugs.launchpad.net/bugs/788986
# Ick.
def bs_fixed_getText(self, separator=u""):
    bsmod = sys.modules[BeautifulSoup.__module__]
    if not len(self.contents):
        return u""
    stopNode = self._lastRecursiveChild().next
    strings = []
    current = self.contents[0]
    while current is not stopNode:
        if isinstance(current, bsmod.NavigableString):
            strings.append(current)
        current = current.next
    return separator.join(strings)
sys.modules[BeautifulSoup.__module__].Tag.getText = bs_fixed_getText
# End fix

def canonicalize_url(url):
    return url.split('?')[0].split('#')[0].strip()

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

def url_to_filename(url):
    return strip_prefix(url, 'http://').rstrip('/')

def grab_url(url, max_depth=5, opener=None):
    if opener is None:
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    retry = False
    try:
        text = opener.open(url, timeout=5).read()
        if '<title>NY Times Advertisement</title>' in text:
            retry = True
    except socket.timeout:
        retry = True
    if retry:
        if max_depth == 0:
            raise Exception('Too many attempts to download %s' % url)
        time.sleep(0.5)
        return grab_url(url, max_depth-1, opener)
    return text

def strip_whitespace(text):
    lines = text.split('\n')
    return '\n'.join(x.strip().rstrip(u'\xa0') for x in lines).strip() + '\n'

# from http://stackoverflow.com/questions/5842115/converting-a-string-which-contains-both-utf-8-encoded-bytestrings-and-codepoints
# Translate a unicode string containing utf8
def parse_double_utf8(txt):
    def parse(m):
        try:
            return m.group(0).encode('latin1').decode('utf8')
        except UnicodeDecodeError:
            return m.group(0)
    return re.sub(ur'[\xc2-\xf4][\x80-\xbf]+', parse, txt)

def canonicalize(text):
    return strip_whitespace(parse_double_utf8(text))

# End utility functions



#Article urls for a single website
def find_article_urls(feeder_url, filter_article, SoupVersion=BeautifulSoup):
    html = grab_url(feeder_url)
    soup = SoupVersion(html)

    # "or ''" to make None into str
    urls = [a.get('href') or '' for a in soup.findAll('a')]

    domain = '/'.join(feeder_url.split('/')[:3])
    urls = [url if '://' in url else domain + url for url in urls]
    return [url for url in urls if filter_article(url)]

def get_all_article_urls():
    ans = set()
    for feeder in feeders:
        urls = find_article_urls(*feeder)
        ans = ans.union(map(canonicalize_url, urls))
    return ans

#Parser for NYT articles
#also used as a base class for other parsers; probably should be split
class Article(object):
    url = None
    title = None
    date = None
    body = None
    byline = None
    real_article = True
    meta = []
    SUFFIX = '?pagewanted=all'

    def __init__(self, url):
        self.url = url
        try:
            self.html = grab_url(url + self.SUFFIX)
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.real_article = False
                return
            raise
        open('/tmp/moo', 'w').write(self.html)
        open('/tmp/moo3', 'w').write(url+self.SUFFIX)
        self._parse(self.html)

    def _parse(self, html):
        logger.debug('got html')
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.meta = soup.findAll('meta')
        self.seo_title = soup.find('meta', attrs={'name':'hdl'}).get('content')
        tmp = soup.find('meta', attrs={'name':'hdl_p'})
        if tmp and tmp.get('content'):
            self.title = tmp.get('content')
        else:
            self.title = self.seo_title
        self.date = soup.find('meta', attrs={'name':'dat'}).get('content')
        self.byline = soup.find('meta', attrs={'name':'byl'}).get('content')
        p_tags = soup.findAll('p', attrs={'itemprop':'articleBody'})
        self.body = '\n'.join([p.getText() for p in p_tags])
        authorids = soup.find('div', attrs={'class':'authorIdentification'})
        self.authorid = authorids.getText() if authorids else ''

        self.top_correction = '\n'.join(x.getText() for x in
                                   soup.findAll('nyt_correction_top')) or '\n'
        self.bottom_correction = '\n'.join(x.getText() for x in
                                   soup.findAll('nyt_correction_bottom')) or '\n'

    def __unicode__(self):
        return canonicalize(u'\n'.join((self.date, self.title, self.byline,
                                            self.top_correction, self.body,
                                            self.authorid,
                                            self.bottom_correction,)))

class CNNArticle(Article):
    SUFFIX = ''

    def _parse(self, html):
        logger.debug('got html')
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        logger.debug('parsed')
        p_tags = soup.findAll('p', attrs={'class':re.compile(r'\bcnn_storypgraphtxt\b')})
        if not p_tags:
            self.real_article = False
            return

        self.meta = soup.findAll('meta')
        self.title = soup.find('meta', attrs={'itemprop':'headline'}).get('content')
        datestr = soup.find('meta', attrs={'itemprop':'dateModified'}).get('content')
        date = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=4)
        self.date = date.strftime(DATE_FORMAT)
        self.byline = soup.find('meta', attrs={'itemprop':'author'}).get('content')
        lede = p_tags[0].previousSibling.previousSibling

        editornotes = soup.findAll('p', attrs={'class':'cnnEditorialNote'})
        contributors = soup.findAll('p', attrs={'class':'cnn_strycbftrtxt'})
        

        self.body = '\n'+'\n\n'.join([p.getText() for p in
                                      editornotes + [lede] + p_tags + contributors])
        authorids = soup.find('div', attrs={'class':'authorIdentification'})

    def __unicode__(self):
        return canonicalize(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))


class PoliticoArticle(Article):
    SUFFIX = ''

    def _parse(self, html):
        logger.debug('got html 1')
        soup = bs4.BeautifulSoup(html)
        print_link = soup.findAll('a', text='Print')[0].get('href')
        html2 = grab_url(print_link)
        logger.debug('got html 2')
        # Now we have to switch back to bs3.  Hilarious.
        # and the labeled encoding is wrong, so force utf-8.
        soup = BeautifulSoup(html2, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        p_tags = soup.findAll('p')[1:]

        self.title = soup.find('strong').getText()
        entity = soup.find('span', attrs={'class':'author'})
        children = list(entity.childGenerator())
        self.byline = 'By ' + children[1].getText()
        datestr = children[-1].strip()
        self.date = datestr

        self.body = '\n'+'\n\n'.join([p.getText() for p in p_tags])

    def __unicode__(self):
        return canonicalize(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))


class BBCArticle(Article):
    SUFFIX = '?print=true'

    def _parse(self, html):
        logger.debug('got html')
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        logger.debug('parsed')

        self.meta = soup.findAll('meta')
        self.title = soup.find('h1', 'story-header').getText()
        self.byline = ''

        div = soup.find('div', 'story-body')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator() if
                                 isinstance(x, Tag) and x.name == 'p'])

        self.date = soup.find('span', 'date').getText()

    def __unicode__(self):
        return canonicalize(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))



# NYT blogs
# currently broken
class BlogArticle(Article):
    SUFFIX = '?pagemode=print'


    def _parse(self, html):
        div_id = url_to_filename(self.url).split('.')
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.document = soup.find('div', attrs={'id':div_id})

    def __unicode__(self):
        return canonicalize(self.document.getText())


class TagesschauArticle(Article):
    SUFFIX = ''

    def _parse(self, html):
        soup = bs4.BeautifulSoup(html)

        # extract the important text of the article into self.document #
        # select the one article
        article = soup.select('div.article')[0]
        # removing comments
        for x in self.descendants(article):
            if isinstance(x, bs4.Comment):
                x.extract()
        # removing elements which don't provide content
        for selector in ('.inv .teaserImg #seitenanfang .spacer .clearMe '+
            '.boxMoreLinks .metaBlock .weltatlas .fPlayer .zitatBox .flashaudio').split(' '):
            for x in article.select(selector):
                x.extract()
        # put hrefs into text form cause hrefs are important content
        for x in article.select('a'):
            x.append(" ["+x.get('href','')+"]")
        # ensure proper formating for later use of get_text()
        for x in article.select('li'):
            x.append("\n")
        for tag in 'p h1 h2 h3 h4 h5 ul div'.split(' '):
            for x in article.select(tag):
                x.append("\n\n")
        # strip multiple newlines away
        import re
        article = re.subn('\n\n+', '\n\n', article.get_text())[0]
        # important text is now extracted into self.document
        self.document = article

        self.title = soup.find('h1').get_text()

        # a by-line is not always there, but when it is, it is em-tag and
        # begins with the word 'Von'
        byline = soup.find('em')
        if byline:
            byline = byline.get_text()
            if 'Von ' not in byline: byline = None
        if not byline: byline = "nicht genannt"
        self.byline = byline

        # TODO self.date is unused, isn't it? but i still fill it here
        date = soup.select("div.standDatum")
        self.date = date and date[0].get_text() or ''

    # XXX a bug in bs4 that tag.descendants isnt working when .extract is called??
    # TODO investigate and report
    @staticmethod
    def descendants(tag):
        x = tag.next_element
        while x:
            next = x.next_element or x.parent and x.parent != tag and x.parent.next_sibling
            yield x
            x = next

    def __unicode__(self):
        return self.document


feeders = [('http://www.nytimes.com/',
            lambda url: 'www.nytimes.com/201' in url),
           ('http://edition.cnn.com/',
            lambda url: 'edition.cnn.com/201' in url),
           ('http://www.politico.com/',
            lambda url: 'www.politico.com/news/stories' in url,
            bs4.BeautifulSoup),
           ('http://www.bbc.co.uk/news/',
            lambda url: 'www.bbc.co.uk/news' in url),
           ]

DomainNameToClass = {'www.nytimes.com': Article,
#                     'opinionator.blogs.nytimes.com': BlogArticle,
#                     'krugman.blogs.nytimes.com': BlogArticle,
                     'edition.cnn.com': CNNArticle,
                     'www.politico.com': PoliticoArticle,
                     'www.bbc.co.uk': BBCArticle,
                     'www.tagesschau.de': TagesschauArticle,
                     }

def get_parser(url):
    return DomainNameToClass[url_to_filename(url).split('/')[0]]


CHARSET_LIST = """EUC-JP GB2312 EUC-KR Big5 SHIFT_JIS windows-1252
IBM855
IBM866
ISO-8859-2
ISO-8859-5
ISO-8859-7
KOI8-R
MacCyrillic
TIS-620
windows-1250
windows-1251
windows-1253
windows-1255""".split()
def is_boring(old, new):
    oldu = canonicalize(old.decode('utf8'))
    newu = canonicalize(new.decode('utf8'))

    if oldu.splitlines()[1:] == newu.splitlines()[1:]:
        return True

    for charset in CHARSET_LIST:
        try:
            if oldu.encode(charset) == new:
                logger.debug('Boring!')
                return True
        except UnicodeEncodeError:
            pass
    return False

def get_diff_info(old, new):
    dmp = diff_match_patch.diff_match_patch()
    dmp.Diff_Timeout = 3 # seconds; default of 1 is too little
    diff = dmp.diff_main(old, new)
    dmp.diff_cleanupSemantic(diff)
    chars_added   = sum(len(text) for (sign, text) in diff if sign == 1)
    chars_removed = sum(len(text) for (sign, text) in diff if sign == -1)
    return dict(chars_added=chars_added, chars_removed=chars_removed)

def add_to_git_repo(data, filename, article):
    start_time = time.time()

    full_path = os.path.join(models.GIT_DIR, filename)
    mkdir_p(os.path.dirname(full_path))

    boring = False
    diff_info = None

    try:
        previous = subprocess.check_output([GIT_PROGRAM, 'show', 'HEAD:'+filename], cwd=models.GIT_DIR, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        if e.output.endswith("does not exist in 'HEAD'\n"):
            already_exists = False
        else:
            raise
    else:
        already_exists = True


    open(full_path, 'w').write(data)

    if already_exists:
        if previous == data:
            return None, None, None

        #Now check how many times this same version has appeared before
        my_hash = subprocess.check_output([GIT_PROGRAM, 'hash-object',
                                        filename], cwd=models.GIT_DIR).strip()

        commits = [v.v for v in article.versions()]
        if len(commits) > 2:
            logger.debug('Checking for duplicates among %s commits',
                          len(commits))
            def get_hash(version):
                """Return the SHA1 hash of filename in a given version"""
                output = subprocess.check_output([GIT_PROGRAM, 'ls-tree', '-r',
                                                  version, filename],
                                                 cwd=models.GIT_DIR)
                return output.split()[2]
            hashes = map(get_hash, commits)

            number_equal = sum(1 for h in hashes if h == my_hash)

            logger.debug('Got %s', number_equal)

            if number_equal >= 2: #Refuse to list a version more than twice
                subprocess.check_output([GIT_PROGRAM, 'checkout', filename],
                                        cwd=models.GIT_DIR)
                return None, None, None

        if is_boring(previous, data):
            boring = True
        else:
            diff_info = get_diff_info(previous, data)

    subprocess.check_output([GIT_PROGRAM, 'add', filename], cwd=models.GIT_DIR)
    if not already_exists:
        commit_message = 'Adding file %s' % filename
    else:
        commit_message = 'Change to %s' % filename
    logger.debug('Running git commit... %s', time.time()-start_time)
    subprocess.check_output([GIT_PROGRAM, 'commit', filename,
                             '-m', commit_message,
                             ],
                    cwd=models.GIT_DIR)
    logger.debug('git revlist... %s', time.time()-start_time)

    # Now figure out what the commit ID was.
    # I would like this to be "git rev-list HEAD -n1 filename"
    # unfortunately, this command is slow: it doesn't abort after the 
    # first line is output.  Without filename, it does abort.
    v = subprocess.check_output([GIT_PROGRAM, 'rev-list', 'HEAD', '-n1'],
                                cwd=models.GIT_DIR).strip()
    logger.debug('done %s', time.time()-start_time)
    return v, boring, diff_info


def load_article(url):
    try:
        parser = get_parser(url)
    except KeyError:
        logger.info('Unable to parse domain, skipping')
        return
    try:
        parsed_article = parser(url)
    except (AttributeError, urllib2.HTTPError, httplib.HTTPException), e:
        if isinstance(e, urllib2.HTTPError) and e.msg == 'Gone':
            return
        logger.error('Exception when parsing %s', url)
        logger.error(traceback.format_exc())
        logger.error('Continuing')
        return
    if not parsed_article.real_article:
        return
    return parsed_article

#Update url in git
#Return whether it changed
def update_article(article):
    parsed_article = load_article(article.url)
    if parsed_article is None:
        return
    to_store = unicode(parsed_article).encode('utf8')
    t = datetime.now()

    v, boring, diff_info = add_to_git_repo(to_store,
                                           url_to_filename(article.url),
                                           article)
    if v:
        logger.info('Modifying! new blob: %s', v)
        v_row = models.Version(v=v,
                               boring=boring,
                               title=parsed_article.title,
                               byline=parsed_article.byline,
                               date=t,
                               article=article,
                               )
        v_row.diff_info = diff_info
        v_row.save()
        if not boring:
            article.last_update = t
            article.save()

def update_articles():
    for url in get_all_article_urls():
        if not models.Article.objects.filter(url=url).count():
            models.Article(url=url).save()

def get_update_delay(minutes_since_update):
    days_since_update = minutes_since_update // (24 * 60)
    if minutes_since_update < 60*3:
        return 15
    elif days_since_update < 1:
        return 30
    elif days_since_update < 7:
        return 120
    elif days_since_update < 30:
        return 60*24
    else:
        return 60*24*7

def update_versions(do_all=False):
    articles = list(models.Article.objects.all())
    total_articles = len(articles)

    update_priority = lambda x: x.minutes_since_check() * 1. / get_update_delay(x.minutes_since_update())
    articles = sorted([a for a in articles if (update_priority(a) > 1 or do_all)], key=update_priority, reverse=True)

    logger.info('Checking %s of %s articles', len(articles), total_articles)
    for i, article in enumerate(articles):
        logger.debug('Woo: %s %s %s (%s/%s)', article.minutes_since_update(), article.minutes_since_check(), update_priority(article), i+1, len(articles))
        delay = get_update_delay(article.minutes_since_update())
        if article.minutes_since_check() < delay and not do_all:
            continue
        logger.info('Considering %s', article.url)
        article.last_check = datetime.now()
        try:
            update_article(article)
        except Exception, e:
            if isinstance(e, subprocess.CalledProcessError):
                logger.error('CalledProcessError when updating %s', article.url)
                logger.error(repr(e.output))
            else:
                logger.error('Unknown exception when updating %s', article.url)

            logger.error(traceback.format_exc())
        article.save()
    subprocess.call([GIT_PROGRAM, 'gc'], cwd=models.GIT_DIR)
    logger.info('Done!')

#Remove index.lock if 5 minutes old
def cleanup_git_repo():
    fname = os.path.join(models.GIT_DIR, '.git/index.lock')
    try:
        stat = os.stat(fname)
    except OSError:
        return
    age = time.time() - stat.st_ctime
    if age > 60*5:
        os.remove(fname)

if __name__ == '__main__':
    print >>sys.stderr, "Try `python website/manage.py scraper`."
