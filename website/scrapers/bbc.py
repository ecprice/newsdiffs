from . import *
from BeautifulSoup import BeautifulSoup, Tag

class BBCArticle(Article):
    SUFFIX = '?print=true'
    domain = 'www.bbc.co.uk'
    fetcher_url = 'http://www.bbc.co.uk/news/'
    @staticmethod
    def article_url_filter(url): return 'www.bbc.co.uk/news' in url

    def _parse(self, html):
        print 'got html'
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        print 'parsed'

        self.meta = soup.findAll('meta')
        self.title = soup.find('h1', 'story-header').getText()
        self.byline = ''

        div = soup.find('div', 'story-body')
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator() if
                                 isinstance(x, Tag) and x.name == 'p'])

        self.date = soup.find('span', 'date').getText()

    def __unicode__(self):
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))

