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
        elt = soup.find('meta', {'property':'og:title'})
        if elt is None:
            self.real_article = False
            return
	else: elt = elt['content']
        self.title = elt
        elbyline = soup.find('div', {'class':'authorProfileContainer'})
	if elbyline is None:
        	elbyline = ''
	else:
		elbyline = elbyline.getText()
	self.byline = elbyline
        edate = soup.find('time', {'class':'timeformat'})
	if edate is None:
            self.real_article = False
            return
	self.date= edate['datetime']

        div = soup.find('div', {'id':'wrapper'})
	intro = soup.find('section', {'class':'body'})
        if div is None:
            # Hack for video articles
            div = soup.find('div', 'emp-decription')
        if div is None:
            self.real_article = False
            return
	if intro is not None:
            self.body = '\n'+'\n\n'.join([x.getText() for x in intro.childGenerator()
                                      if isinstance(x, Tag) and x.name=='ul'])	
        self.body += '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name=='p'])
