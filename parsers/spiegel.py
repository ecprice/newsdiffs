from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup

class SpiegelParser(BaseParser):
    SUFFIX = ''
    domains = ['www.spiegel.de']

    feeder_pat   = '^http://www.spiegel.de/(politik|wirtschaft|panorama|netzwelt|gesundheit)/[a-z]'
    feeder_pages = ['http://www.spiegel.de/schlagzeilen/index.html']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        #article headline
        elt = soup.find('h2', {'class': 'article-title'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        try:
            author = soup.find('a', {'rel': 'author'}).text
        except:
            author = ''
        self.byline = author
        # article date
        created_at = soup.find('meta', {'name': 'date'})['content']
        self.date = created_at if created_at else ''
        #article content
        div = soup.find('div', 'article-section clearfix')
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        text = ''
        p = div.findAll('p')
        for txt in p:
            text += txt.getText()+'\n'
        self.body = text
