from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NTVParser(BaseParser):
    domains = ['www.n-tv.de']

    feeder_pat = '^http://www.n-tv.de/(politik|wirtschaft|panorama|technik|wissen)/.*article\d*'
    feeder_pages = ['http://www.n-tv.de']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        if soup.find('title').getText().find('Mediathek'):
            self.real_article = False
            return
        #article headline
        elt = soup.find('h1', {'class': 'h1'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        author = soup.find('p', {'class': 'author'})
        self.byline = author.getText() if author else ''
        # article date
        created_at = soup.find('div', {'itemprop': 'date-published'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('div', {'class': 'content'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        map(lambda x: x.extract(), div.findAll('p', {'class': 'author'}))
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])
