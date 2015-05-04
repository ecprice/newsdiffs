from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class BildParser(BaseParser):
    SUFFIX = ''
    domains = ['www.bild.de']

    feeder_pat   = '^http://www.bild.de/(politik|regional|geld|digital)'
    feeder_pages = ['http://www.bild.de/politik/startseite',
                    'http://www.bild.de/geld/startseite/',
                    'http://www.bild.de/regional/startseite/',
                    'http://www.bild.de/digital/startseite/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('meta', {'property': 'og:title'})['content']
        if elt is None:
            self.real_article = False
            return
        self.title = elt
        created_at = soup.find('div', {'class': 'date'}).getText()
        self.date = created_at if created_at else ''
        author = soup.find('div', {'itemprop':'author'})
        self.byline = author.getText() if author else ''
        print(self.byline)
        div = soup.find('div', {'itemprop':'articleBody isFamilyFriendly'})
        if div is None:
            self.real_article = False
            return
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
        self.body = text

