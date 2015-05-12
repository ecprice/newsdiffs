from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class RPOParser(BaseParser):
    domains = ['www.rp-online.de']

    feeder_pat = '1\.\d*$'
    feeder_pages = ['http://www.rp-online.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        #article headline
        elt = soup.find('meta', {'property': 'og:title'})['content']
        if elt is None:
            self.real_article = False
            return
        self.title = elt
        # byline / author
        author = soup.find('meta', {'itemprop': 'author'})['content']
        self.byline = author if author else ''
        # article date
        created_at = soup.find('meta', {'property': 'vr:published_time'})['content']
        self.date = created_at if created_at else ''
        #article content
        div = soup.find('div', {'class': 'main-text '})
        intro = soup.find('div', {'class': 'first intro'})
        if intro is None:
            intro = ''
        else:
            intro = intro.find('strong').getText()
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        self.body = intro
        self.body += '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                         if isinstance(x, Tag) and x.name == 'p'])
