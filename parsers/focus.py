from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class FocusParser(BaseParser):
    SUFFIX = ''
    domains = ['www.focus.de']

    feeder_pat   = '^http://www.focus.de/(politik|finanzen|panorama|gesundheit|wissen)'
    feeder_pages = ['http://www.focus.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h1', 'articleIDentH1')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        self.byline = ''
        self.date = soup.find('span', 'created').getText()


        div = soup.find('div', 'article-body')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
