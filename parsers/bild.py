from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class BildParser(BaseParser):
    SUFFIX = ''
    domains = ['www.bild.de']

    feeder_pat   = '^http://www.bild.de/(politik|regional|geld)'
    feeder_pages = ['http://www.bild.de/news']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find(attrs = {'class' : 'headline'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        print(self.title)
        self.byline = ''
        self.date = soup.find(attrs = {'time' : 'datetime'})
        self.authorids = soup.find('div', attrs={'itemprop':'author'})
        self.byline = self.authorids.getText() if self.authorids else ''

        div = soup.find('div', 'txt').getText()
        print(div)
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
