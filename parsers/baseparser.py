import cookielib
import logging
import re
import socket
import sys
import time
import urllib2

# Define a logger

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



# Utility functions

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




# Begin hot patch for https://bugs.launchpad.net/bugs/788986
# Ick.
from BeautifulSoup import BeautifulSoup
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

def concat(domain, url):
    return domain + url if url.startswith('/') else domain + '/' + url

# End utility functions

# Base Parser
# To create a new parser, subclass and define _parse(html).
class BaseParser(object):
    url = None
    domains = [] # List of domains this should parse

    # These should be filled in by self._parse(html)
    date = None
    title = None
    byline = None
    body = None

    real_article = True # If set to False, ignore this article
    SUFFIX = ''         # append suffix, like '?fullpage=yes', to urls

    meta = []  # Currently unused.

    # Used when finding articles to parse
    feeder_pat   = None # Look for links matching this regular expression
    feeder_pages = []   # on these pages

    feeder_bs = BeautifulSoup #use this version of beautifulsoup for feed

    def __init__(self, url):
        self.url = url
        try:
            self.html = grab_url(self._printableurl())
        except urllib2.HTTPError as e:
            if e.code == 404:
                self.real_article = False
                return
            raise
        logger.debug('got html')
        self._parse(self.html)

    def _printableurl(self):
        return self.url + self.SUFFIX

    def _parse(self, html):
        """Should take html and populate self.(date, title, byline, body)

        If the article isn't valid, set self.real_article to False and return.
        """
        raise NotImplementedError()

    def __unicode__(self):
        return canonicalize(u'\n'.join((self.date, self.title, self.byline,
                                        self.body,)))

    @classmethod
    def feed_urls(cls):
        all_urls = []
        for feeder_url in cls.feeder_pages:
            html = grab_url(feeder_url)
            soup = cls.feeder_bs(html)

            # "or ''" to make None into str
            urls = [a.get('href') or '' for a in soup.findAll('a')]

            # If no http://, prepend domain name
            domain = '/'.join(feeder_url.split('/')[:3])
            urls = [url if '://' in url else concat(domain, url) for url in urls]

            all_urls = all_urls + [url for url in urls if
                                   re.search(cls.feeder_pat, url)]
        return all_urls
