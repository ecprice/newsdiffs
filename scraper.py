#!/usr/bin/python2.7

import sys
import subprocess
import urllib2
from BeautifulSoup import BeautifulSoup
import os
import errno
import models
import re
from datetime import datetime, timedelta

DIFF_DIR = 'articles/'
GIT_DIR = DIFF_DIR + '.git'

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise

# Begin hot patch for https://bugs.launchpad.net/bugs/788986
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
    url = url.strip()+'?'
    return url[:url.find('?')]

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

def url_to_filename(url):
    return strip_prefix(url, 'http://').rstrip('/')

def grab_url(url):
    text = urllib2.urlopen(url).read()
    if '<title>NY Times Advertisement</title>' in text:
        return grab_url(url)
    return text

feeders = [('http://www.nytimes.com/',
            lambda url: 'nytimes.com/201' in url),
           ('http://edition.cnn.com/',
            lambda url: 'edition.cnn.com/201' in url),
               ]

def find_article_urls(feeder_url, filter_article):
    html = grab_url(feeder_url)
    soup = BeautifulSoup(html)

    # "or ''" to make None into str
    urls = [a.get('href') or '' for a in soup.findAll('a')]

    domain = os.path.dirname(feeder_url)
    urls = [url if '://' in url else domain + url for url in urls]
    return [url for url in urls if filter_article(url)]

def get_all_article_urls():
    ans = set()
    for (feeder_url, filter_func) in feeders:
        urls = find_article_urls(feeder_url, filter_func)
        ans = ans.union(map(canonicalize_url, urls))
    return ans

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
        if tmp:
            self.title = tmp.get('content')
        else:
            self.title = self.seo_title
        self.date = soup.find('meta', attrs={'name':'dat'}).get('content')
        self.byline = soup.find('meta', attrs={'name':'byl'}).get('content')
        p_tags = soup.findAll('p', attrs={'itemprop':'articleBody'})
        self.body = '\n'.join([p.getText() for p in p_tags])
        authorids = soup.find('div', attrs={'class':'authorIdentification'})
        self.authorid = authorids.getText() if authorids else ''
        self.top_correction = soup.find('nyt_correction_top').getText()
        self.bottom_correction = soup.find('nyt_correction_bottom').getText()

    def __unicode__(self):
        return u'\n'.join((self.date, self.title, self.byline,
                          self.top_correction, self.body,
                          self.authorid, self.bottom_correction,)).strip()+'\n'


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
        return u'\n'.join((self.date, self.title, self.byline,
                          self.body,)).strip()+'\n'



class BlogArticle(Article):
    SUFFIX = '?pagemode=print'


    def _parse(self, html):
        div_id = url_to_filename(self.url).split('.')
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.document = soup.find('div', attrs={'id':div_id})

    def __unicode__(self):
        return self.document.getText().strip()+'\n'

 
DomainNameToClass = {'www.nytimes.com': Article,
                     'opinionator.blogs.nytimes.com': BlogArticle,
                     'krugman.blogs.nytimes.com': BlogArticle,
                     'edition.cnn.com': CNNArticle,
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

def update_article(url):
    try:
        parser = get_parser(url)
    except KeyError:
        print 'Unable to parse domain, skipping'
        return
    article = parser(url)
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
    days_since_update = minutes_since_update // 24
    if days_since_update < 1:
        return 15
    elif days_since_update < 7:
        return 60
    elif days_since_update < 30:
        return 60*24
    else:
        return 60*24*7


if __name__ == '__main__':
    session = models.Session()
    insert_all_articles(session)
    for article_row in session.query(models.Article).all():
        print 'Woo:', article_row.minutes_since_update(), article_row.minutes_since_check()
        delay = get_update_delay(article_row.minutes_since_update())
        if article_row.minutes_since_check() < delay:
            continue
        print 'Considering', article_row.url
        if update_article(article_row.url):
            print 'Updated!'
            article_row.last_update = datetime.now()
        article_row.last_check = datetime.now()
        session.commit()
