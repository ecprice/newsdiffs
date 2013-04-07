from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NOSNLParser(BaseParser):
    domains = ['www.nos.nl']

    feeder_base = 'http://www.nos.nl'
    feeder_pat  = '^http://www.nos.nl/artikel/'

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')

        article = soup.find('div', id = 'article')
        self.title = article.find('h1').getText()

        article_content = soup.find('div', id = 'article-content')

        self.byline = ''
        self.date = article_content.find('abbr', 'page-last-modified').getText()

        self.body = ''
        for i in article_content.childGenerator():
            if not isinstance(i, Tag):
                continue
            if not i.name == 'p':
                continue

            self.body += i.getText() + '\n\n'

