__author__ = 'krawallmieze'

from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class SDParser(BaseParser):
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
        author = soup.find('a', {'class': 'author person objlink'}) #darin noch ein h4 div> a> h4
        self.byline = author.getText() if author else ''
        # article date
        created_at = soup.find('span', {'class': 'date'})
        if created_at is None:
            self.real_article = False
            return
        self.date = created_at['datetime']
        #article content
        div = soup.find('div', {'class': 'odd sect sect_article news report'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])