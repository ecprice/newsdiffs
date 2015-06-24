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
        #article headline
        elt = soup.find('h1', 'widget storyContent title prefix_1 grid_8')
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        # byline / author
        authorids = soup.find('span', {'itemprop': 'author'})
        self.byline = authorids.getText() if authorids else ''
        # article date
        self.date = soup.find('meta', {'name': 'date'})['content']
        #article content
        div = soup.find('div', 'storyBody')
        #div = self.remove_non_content(div)
        print(div)
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
