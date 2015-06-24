__author__ = 'krawallmieze'

from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class TAZParser(BaseParser):
    domains = ['www.taz.de']

    feeder_pat   = '.+\/!\d{7}'
    feeder_pages = ['http://www.taz.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})
        if elt is None:
            self.real_article = False
            return
        else:
            self.title = elt['content']
        # byline / author
        author = soup.find('meta', {'name': 'author'})
        self.title = author['content'] if author else ''
        # article date
        created_at = soup.find('span', {'class': 'date'})
        if created_at is None:
            self.real_article = False
            return
        self.date = created_at.getText() if created_at else ''
        #category
        self.category = ""

        #self.date = created_at['datetime']
        #article content
        div = soup.find('div', {'class': 'odd sect sect_article news report'}).find('div', {'class': 'sectbody'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        map(lambda x: x.extract(), div.findAll('p', {'class':'caption'}))

        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])