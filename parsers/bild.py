from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class BildParser(BaseParser):
    SUFFIX = ''
    domains = ['www.bild.de']

    feeder_pat   = '^http://www.bild.de/(politik|regional|geld|digital/[a-z])'
    feeder_pages = ['http://www.bild.de/politik/startseite',
                    'http://www.bild.de/geld/startseite/',
                    'http://www.bild.de/regional/startseite/',
                    'http://www.bild.de/digital/startseite/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        #article headline
        try:
            elt = soup.find('meta', {'property': 'og:title'})['content']
            self.title = elt
        except:
            self.real_article = False
            return

        # byline / author
        author = soup.find('div', {'itemprop':'author'})
        self.byline = author.getText() if author else ''
        # article date
        created_at = soup.find('div', {'class': 'date'})
        self.date = created_at.getText() if created_at else ''
        #article content
        div = soup.find('div', {'itemprop':'articleBody isFamilyFriendly'})
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        map(lambda x: x.extract(), div.findAll('div', {'class':'infoEl center edge'})) # commercials
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
        self.body = text

