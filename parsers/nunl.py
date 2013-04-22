from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag


class NuNLParser(BaseParser):
    SUFFIX = ''
    domains = ['www.nu.nl']

    feeder_base = 'http://www.nu.nl/'
    feeder_pat  = '^http://www.nu.nl/\w+/\d+/'

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        header = soup.find('div', 'header')

        self.meta = soup.findAll('meta')
        self.title = header.find('h1').getText()

        self.byline = ''

        # Date of the last revision
        self.date = header.find('div', 'dateplace-data').contents[2].lstrip()

        content = soup.find('div', 'content')

        self.body = ''

        for i in content.childGenerator():
            if not isinstance(i, Tag):
                continue
            if not i.name == 'h2' and not i.name == 'p':
                continue

            self.body += i.getText() + '\n\n'

