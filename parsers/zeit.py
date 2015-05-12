from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class ZeitParser(BaseParser):
    SUFFIX = '?print=true'
    domains = ['www.zeit.de']

    feeder_pat = '^http://www.zeit.de/news/\d'
    feeder_pages = ['http://www.zeit.de/news/index/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        #article headline
        elt = soup.find('span', 'title')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        author = soup.find('span', {'class': 'header_author'})
        self.byline = author.getText() if author else ''
        # article date
        created_at = soup.find('span', 'articlemeta-datetime')
        self.date = created_at.getText() if created_at else ''
        #article content
        div = soup.find('div', 'article-body')
        div = self.remove_non_content(div)
        if div is None:
            self.real_article = False
            return
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])
