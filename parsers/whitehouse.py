import datetime
import dateutil.parser

from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag

DATE_FORMAT = '%A, %B %e %Y, %l:%M %p'

class WhitehouseParser(BaseParser):
    domains = ['www.whitehouse.gov']

    # TODO This pattern isn't finding most blog links. Why?
    feeder_pat   = '(^https://www.whitehouse.gov/)|(^/.*)'
    feeder_pages = [
        'https://www.whitehouse.gov',
        ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        title = soup.find('meta', property='og:title')
        if title is None:
            self.real_article = False
            return
        self.title = title['content']
        self.byline = ''
        self.date = ''
        published_time = dateutil.parser.parse(soup.find('meta', property='article:published_time')['content'])
        if published_time is not None:
          self.date = published_time.strftime(DATE_FORMAT)

        div = soup.find('div', 'pane-node-field-forall-body')
        if div is None:
            self.real_article = False
            return
        self.body = u'\n\n'.join([unicode(x.getText().strip()) for x in div.findAll('p')])
