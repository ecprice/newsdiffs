from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class WhitehouseParser(BaseParser):
    domains = ['www.whitehouse.gov']

    # TODO This pattern isn't finding most blog links. Why?
    feeder_pat   = '(^https://www.whitehouse.gov/)|(^/.*)'
    feeder_pages = [
        'https://www.whitehouse.gov',
        ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('div', 'pane-node-title')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.h1.getText()
        self.byline = ''
        self.date = soup.find('span', 'date').getText()

        div = soup.find('div', 'pane-node-field-forall-body')
        if div is None:
            # Hack for video articles
            div = soup.find('div', 'emp-decription')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
