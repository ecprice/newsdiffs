from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class ZeitParser(BaseParser):
    SUFFIX = '?print=true'
    domains = ['www.zeit.de']

    feeder_pat   = '^http://www.zeit.de/news/\d'
    feeder_pages = ['http://www.zeit.de/news/index/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('span', 'title')
	elTopic = soup.find('span', 'supertitle')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
	elbyline = soup.find('span', {'class':'header_author'})
	if elbyline is None:
        	elbyline = ''
	else:
		elbyline = elbyline.getText()
	self.byline = elbyline
	edate = soup.find('span', 'articlemeta-datetime')
	if edate is None: 
            self.real_article = False
            return
	else: self.date = edate.getText()
        div = soup.find('div', 'article-body')
        if div is None:
            # Hack for video articles
            div = soup.find('div', 'emp-decription')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
