from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class SpiegelParser(BaseParser):
    SUFFIX = ''
    domains = ['www.spiegel.de']

    feeder_pat   = '^http://www.spiegel.de/(politik|wirtschaft|panorama|netzwelt|gesundheit)/'
    feeder_pages = ['http://www.spiegel.de/schlagzeilen/index.html']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h2', attrs={'class':'article-title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        self.byline = ''
        self.date = soup.find(attrs = {'time' : 'datetime'})

        div = soup.find('div', 'article-section')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
