from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup


class FocusParser(BaseParser):
    SUFFIX = '?drucken=1'
    domains = ['www.focus.de']

    feeder_pat   = '^http://www.focus.de/(politik|finanzen|gesundheit|wissen)'
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
        try:
            author = soup.find('a', {'rel':'author'}).text
        except:
            author = ''
        self.byline = author
        created_at = soup.find('meta', {'name':'date'})['content']
        self.date = created_at if created_at else ''
        self.body = ''
        div = soup.find('div', 'articleContent')
        if div is None:
            self.real_article = False
            return
        div = self.remove_non_content(div)
        text = ''
        p = div.findAll('p')
        for txt in p:
                text += txt.getText()+'\n'
        self.body = text