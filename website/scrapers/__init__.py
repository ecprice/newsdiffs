from frontend.management.commands._utils import *

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class Article(object):
    SUFFIX = ''
    domain = ''
    fetcher_url = ''
    article_url_filter = lambda url: True

    def __init__(self, url):
        self.url = url
        self.real_article = True
        self.html = grab_url(url + self.SUFFIX)
        self._parse(self.html)
        
    @classmethod
    def fetch_urls(self):
        return find_article_urls(self.fetcher_url, self.article_url_filter)

#Article urls for a single website
from BeautifulSoup import BeautifulSoup
def find_article_urls(feeder_url, filter_article, SoupVersion=BeautifulSoup):
    html = grab_url(feeder_url)
    soup = SoupVersion(html)

    # "or ''" to make None into str
    urls = [a.get('href') or '' for a in soup.findAll('a')]

    domain = '/'.join(feeder_url.split('/')[:3])
    urls = [url if '://' in url else domain + url for url in urls]
    return [url for url in urls if filter_article(url)]

