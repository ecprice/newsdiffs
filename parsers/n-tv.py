from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NTVParser(BaseParser):
    domains = ['www.n-tv.de']

    feeder_pat = 'article\d+'
    feeder_pages = ['http://www.n-tv.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        #article headline
        elt = soup.find('h1', {'class': 'h1'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        author = soup.find('meta', {'name': 'author'})['content']
        self.byline = author if author else ''
        # article date
        created_at = soup.find('div', {'itemprop': 'date-published'})['content']
        self.date = created_at if created_at else ''
        #article content
        div = soup.find('div', {'class': 'content'})
        div = self.remove_non_content(div)
        if div is None:
            self.real_article = False
            return
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])
