from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class FocusParser(BaseParser):
    SUFFIX = '?drucken=1'
    domains = ['www.focus.de']

    feeder_pat   = '^http://www.focus.de/(politik|finanzen|panorama|gesundheit|wissen)'
    feeder_pages = ['http://www.focus.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h1')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        #self.byline = soup.find('a', {'rel':'author'})
        #self.date = soup.find('meta', {'name':'date'})['content']

        content = soup.find('div', 'articleContent').findAll('div', 'textBlock')
        if content is None:
            self.real_article = False
            return
        text = ''
        for div in content:
            p = div.findAll('p')
            for txt in p:
                text += txt.getText()
        print(text)
        self.body = text