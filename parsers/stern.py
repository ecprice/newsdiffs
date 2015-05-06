from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class SternParser(BaseParser):
    SUFFIX = ''
    domains = ['www.stern.de']

    feeder_pat   = '^http://www.stern.de/(politik|wirtschaft|panorama|lifestyle|wissen|digital)/'
    feeder_pages = ['http://www.stern.de/news',
                    'http://www.stern.de/news/2',
                    'http://www.stern.de/news/3',
                    'http://www.stern.de/news/4'
                    ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h2', {'id':'div_article_headline'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        self.byline = ''        # no author on stern.de
        created_at = soup.find('meta', {'name':'last-modified'})
        self.date = created_at['content'] if created_at else ''

        div = soup.find('div', {'itemprop':'mainContentOfPage'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
        self.body = text