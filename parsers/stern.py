from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class SternParser(BaseParser):
    SUFFIX = ''
    domains = ['www.stern.de']

    feeder_pat   = '^http://www.stern.de/(politik|wirtschaft|panorama|lifestyle|wissen|digital)/'
    feeder_pages = ['http://www.stern.de/news']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        elt = soup.find('h2', attrs={'id':'div_article_headline'})
        if elt is None:
            self.real_article = False
            return
        self.title = elt.getText()
        self.byline = ''
        self.date = soup.find('div', attrs = {'class' : 'datePublished'})

        div = soup.find('span', attrs={'itemprop':'articleBody'})
        print(div)
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText() for x in div.childGenerator()
                                      if isinstance(x, Tag) and x.name == 'p'])
