#!/usr/bin/python2.7

import sys
import subprocess
import urllib2
from BeautifulSoup import BeautifulSoup
import os
import errno
import models

DIFF_DIR = 'articles/'
GIT_DIR = DIFF_DIR + '.git'

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


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


def canonicalize_url(url):
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

feeder_urls = ['http://www.nytimes.com/', 'http://www.nytimes.com/pages/opinion/index.html']
def nyt_filter(url):
    return url and 'nytimes.com/201' in url


def find_article_urls(html, filter_article):
    soup = BeautifulSoup(html)
    urls = [a.get('href') for a in soup.findAll('a')]
    return [url for url in urls if filter_article(url)]

def get_all_article_urls():
    ans = set()
    for feeder_url in feeder_urls:
        urls = find_article_urls(grab_url(feeder_url), nyt_filter)
        ans = ans.union(map(canonicalize_url, urls))
    return ans

class Article(object):
    url = None
    title = None
    date = None
    body = None
    meta = []
    SUFFIX = '?pagewanted=all'

    def __init__(self, url):
        self.url = url
        self.html = grab_url(url + self.SUFFIX)
        open('/tmp/moo', 'w').write(self.html)
        open('/tmp/moo3', 'w').write(url)
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
                          self.authorid, self.bottom_correction,))

class BlogArticle(Article):
    SUFFIX = '?pagemode=print'


    def _parse(self, html):
        div_id = url_to_filename(self.url).split('.')
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.document = soup.find('div', attrs={'id':div_id})

    def __unicode__(self):
        return self.document.getText()

 
DomainNameToClass = {'www.nytimes.com': Article,
                     'opinionator.blogs.nytimes.com': BlogArticle,
                     'krugman.blogs.nytimes.com': BlogArticle,
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
    to_store = unicode(article).encode('utf8')
    return add_to_git_repo(to_store, url_to_filename(url))


def insert_all_articles(session):
    for url in get_all_article_urls():
        if session.query(models.Article).filter_by(url=url).first() is None:
            session.add(models.Article(url))
    session.commit()



if __name__ == '__main__':
    session = models.Session()
    insert_all_articles(session)
    for article_row in session.query(models.Article).all():
        if article_row.minutes_since_update() < 10:
            continue
        print 'Considering', article_row.url
        if update_article(article_row.url):
            print 'Updated!'
            article_row.update()
            session.commit()
