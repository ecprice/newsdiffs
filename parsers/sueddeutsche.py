from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class SDParser(BaseParser):
    domains = ['www.sueddeutsche.de']

    feeder_pat   = '1\.\d*$'
    feeder_pages = ['http://www.sueddeutsche.de/']

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
        author = soup.find('div', {'class': 'authorProfileContainer'})
        self.byline = author.getText() if author else ''
        # article date
        created_at = soup.find('time', {'class': 'timeformat'})
        if created_at is None:
            self.real_article = False
            return
        self.date = created_at['datetime']
        #article content
        div = soup.find('div', {'id': 'wrapper'})
        intro = soup.find('section', {'class': 'body'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        if intro is not None:
            self.body = '\n' + '\n\n'.join([x.getText() for x in intro.childGenerator()
                                            if isinstance(x, Tag) and x.name == 'ul'])
        self.body += '\n' + '\n\n'.join([x.getText() for x in div.childGenerator()
                                         if isinstance(x, Tag) and x.name == 'p'])
