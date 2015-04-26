from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class WeltParser(BaseParser):
    SUFFIX = '?config=print'
    domains = ['www.welt.de']

    feeder_pat   = '^http://www.welt.de/(politik|wirtschaft|panorama|geld|wissen|regional)/'
    feeder_pages = ['http://www.welt.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h1')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        self.byline = ''
        self.date = soup.find('div', attrs = {'id' : 'currenttime'})
        self.authorids = soup.find('span', attrs={'itemprop':'author'})
        self.authorid = self.authorids.getText() if self.authorids else ''

        div = soup.find('div', 'storyBody')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
