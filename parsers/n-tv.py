from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NTVParser(BaseParser):
    domains = ['www.n-tv.de']

    feeder_pat = '^http://www.n-tv.de/(politik|wirtschaft|panorama|technik|wissen)/[a-z]'
    feeder_pages = ['http://www.n-tv.de/politik',
                    'http://www.n-tv.de/wirtschaft',
                    'http://www.n-tv.de/panorama',
                    'http://www.n-tv.de/technik',
                    'http://www.n-tv.de/wissen',
                    ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        if soup.find('strong', {'class': 'category'})=='mediathek':
            self.real_article = False
            return
        #article headline
        elt = soup.find('h1', {'class': 'h1'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        author = soup.find('meta', {'name': 'author'})
        self.byline = author['content'] if author else ''
        # article date
        created_at = soup.find('div', {'itemprop': 'date-published'})
        self.date = created_at['content'] if created_at else ''
        #article content
        div = soup.find('div', {'class': 'content'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        self.body = '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                        if isinstance(x, Tag) and x.name == 'p'])
