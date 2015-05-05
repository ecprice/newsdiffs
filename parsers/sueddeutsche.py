from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class SDParser(BaseParser):
    domains = ['http://www.sueddeutsche.de/']

    feeder_pat   = '1\.\d*$'
    feeder_pages = ['http://www.sueddeutsche.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        self.meta = soup.findAll('meta')
        elt = soup.find('meta', {'property':'og:title'})['content']
        if elt is None:
            self.real_article = False
            return
        self.title = elt
        self.byline = ''
        self.date = soup.find('time', {'class':'timeformat'})['datetime']

        div = soup.find('div', {'id':'wrapper'})
	intro = soup.find('section', {'class':'body'})

        if div is None:
            # Hack for video articles
            div = soup.find('div', 'emp-decription')
        if div is None:
            self.real_article = False
            return
	self.body = '\n'+'\n\n'.join([x.getText() for x in intro.childGenerator()
                                      if isinstance(x, Tag) and x.name=='ul'])
        self.body += '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name=='p'])
