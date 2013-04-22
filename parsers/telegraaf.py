from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag, Comment


class TelegraafParser(BaseParser):
    domains = ['www.telegraaf.nl']

    feeder_base = 'http://www.telegraaf.nl'
    feeder_pat  = '^http://www.telegraaf.nl/\w+/\d+/'

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')

        article = soup.find('div', id = 'artikel')
        title = article.find('h1')

        self.title = ''
        for i in title.childGenerator():
            # Skip comments
            if isinstance(i, Comment):
                continue

            self.title += i.lstrip()

        self.byline = ''

        date = article.find('div', 'artDatePostings')
        self.date = date.find('span', 'datum').getText()

        article_column = soup.find('div', id = 'artikelKolom')

        self.body = ''
        for i in article_column.childGenerator():
            if not isinstance(i, Tag):
                continue
            if not i.name == 'p':
                continue
            self.body += i.getText() + '\n\n'
