#!/usr/bin/python

import sys
import subprocess
import urllib2
import httplib
import os
import errno
import models
import re
from datetime import datetime, timedelta
import traceback

# Different versions of BeautifulSoup have different properties.
# Some work with one site, some with another.
# This is BeautifulSoup 3.2.
from BeautifulSoup import BeautifulSoup
# This is BeautifulSoup 4
import bs4


DIFF_DIR = 'articles/'
GIT_DIR = DIFF_DIR + '.git'

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
        raise CalledProcessError(retcode, cmd, output=output)
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

def grab_url(url):
    text = urllib2.urlopen(url).read()
    # Occasionally need to retry
    if '<title>NY Times Advertisement</title>' in text:
        return grab_url(url)
    return text

def strip_whitespace(text):
    lines = text.split('\n')
    return '\n'.join(x.strip().rstrip(u'\xa0') for x in lines).strip() + '\n'

# End utility functions



feeders = [('http://www.nytimes.com/',
            lambda url: 'nytimes.com/201' in url),
           ('http://edition.cnn.com/',
            lambda url: 'edition.cnn.com/201' in url),
           ('http://www.politico.com/',
            lambda url: 'www.politico.com/news/stories' in url,
            bs4.BeautifulSoup),
               ]

#Article urls for a single website
def find_article_urls(feeder_url, filter_article, SoupVersion=BeautifulSoup):
    html = grab_url(feeder_url)
    soup = SoupVersion(html)

    # "or ''" to make None into str
    urls = [a.get('href') or '' for a in soup.findAll('a')]

    domain = os.path.dirname(feeder_url)
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
    real_article = True
    meta = []
    SUFFIX = '?pagewanted=all'

    def __init__(self, url):
        self.url = url
        self.html = grab_url(url + self.SUFFIX)
        open('/tmp/moo', 'w').write(self.html)
        open('/tmp/moo3', 'w').write(url+self.SUFFIX)
        self._parse(self.html)

    def _parse(self, html):
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
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
                                            self.top_correction, self.body,
                                            self.authorid,
                                            self.bottom_correction,)))

# XXX CNN might have an issue with unicode
class CNNArticle(Article):
    SUFFIX = ''

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
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
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))


class PoliticoArticle(Article):
    SUFFIX = ''

    def _parse(self, html):
        soup = bs4.BeautifulSoup(html)
        print_link = soup.findAll('a', text='Print')[0].get('href')
        html2 = grab_url(print_link)
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
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
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
        return strip_whitespace(self.document.getText())

DomainNameToClass = {'www.nytimes.com': Article,
                     'opinionator.blogs.nytimes.com': BlogArticle,
                     'krugman.blogs.nytimes.com': BlogArticle,
                     'edition.cnn.com': CNNArticle,
                     'www.politico.com': PoliticoArticle,
                     }

def get_parser(url):
    for key in DomainNameToClass:
        if url_to_filename(url).startswith(key):
            return DomainNameToClass[key]
    raise KeyError(url)


def add_to_git_repo(data, filename):

    mkdir_p(os.path.dirname(DIFF_DIR+filename))

    already_exists = os.path.exists(DIFF_DIR+filename)
    open(DIFF_DIR+filename, 'w').write(data)
    if not already_exists:
        subprocess.call(['/usr/bin/git', 'add', filename], cwd=DIFF_DIR)
        commit_message = 'Added %s' % filename
        return_value = 2
    else:
        if not subprocess.check_output(['/usr/bin/git', 'ls-files', '-m', filename], cwd=DIFF_DIR):
            return 0
        return_value = 1
        commit_message = 'Change to %s' % filename
    subprocess.call(['/usr/bin/git', 'commit', filename, '-m', commit_message], cwd=DIFF_DIR)
    return return_value

#Update url in git
#Return whether it changed
def update_article(url):
    try:
        parser = get_parser(url)
    except KeyError:
        print 'Unable to parse domain, skipping'
        return
    try:
        article = parser(url)
    except (AttributeError, urllib2.HTTPError, httplib.HTTPException), exc:
        print 'Exception when parsing', url
        traceback.print_exc()
        print 'Continuing'
        return -1
    if not article.real_article:
        return 0
    to_store = unicode(article).encode('utf8')
    return add_to_git_repo(to_store, url_to_filename(url))


def insert_all_articles(session):
    for url in get_all_article_urls():
        if session.query(models.Article).filter_by(url=url).first() is None:
            session.add(models.Article(url))
    session.commit()


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


if __name__ == '__main__':
    session = models.Session()
    insert_all_articles(session)
    num_articles = session.query(models.Article).count()
    articles = session.query(models.Article).order_by(models.Article.last_check).all()
    for i, article_row in enumerate(articles):
        print 'Woo:', article_row.minutes_since_update(), article_row.minutes_since_check(), '(%s/%s)' % (i+1, num_articles)
        delay = get_update_delay(article_row.minutes_since_update())
        if article_row.minutes_since_check() < delay:
            continue
        print 'Considering', article_row.url
        retcode = update_article(article_row.url)
        if retcode > 1:
            print 'Updated!'
            article_row.last_update = datetime.now()
        if retcode >= 0:
            article_row.last_check = datetime.now()
        session.commit()
