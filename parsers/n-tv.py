from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NTVParser(BaseParser):

    domains = ['www.n-tv.de']

    feeder_pat   = 'article\d+'
    feeder_pages = ['http://www.n-tv.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')      
	self.meta = soup.findAll('meta')
        elt = soup.find('h1', {'class':'h1'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        ebyline = soup.find('meta', {'name':'author'})
	if ebyline is None:
            self.byline = ''
	else: self.byline = ebyline['content']
	edate = soup.find('meta', {'name':'last-modified'})
	if edate is None:
            self.real_article = False
            return
	self.date= edate['content']
        div = soup.find('div', {'class':'content'})
        if div is None:
            # Hack for video articles
            div = soup.find('div', 'emp-decription')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
