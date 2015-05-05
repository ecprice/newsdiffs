from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class FAZParser(BaseParser):
    domains = ['www.faz.net']

    feeder_pat   = 'aktuell/.*\.html$'
    feeder_pages = ['http://www.faz.net/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        elt = soup.find('meta', {'property':'og:title'})['content']
        if elt is None:
            self.real_article = False
            return
        self.title = elt
        self.byline = ''
        self.date = soup.find('meta', {'name':'last-modified'})['content']

        div = soup.find('div', 'FAZArtikelContent').find('div', {'class':''})
        if div is None:
            # Hack for video articles
            div = soup.find('div', 'emp-decription')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
