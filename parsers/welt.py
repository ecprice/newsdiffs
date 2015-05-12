from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class WeltParser(BaseParser):

    domains = ['www.welt.de']

    feeder_pat   = 'article\d*'
    feeder_pages = ['http://www.welt.de/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h1', 'widget storyContent title prefix_1 grid_8')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()

        authorids = soup.find('span', attrs={'itemprop': 'author'})
        self.byline = authorids.getText() if authorids else ''
        self.date = soup.find('meta', {'name': 'date'})['content']

        div = soup.find('div', 'storyBody')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
