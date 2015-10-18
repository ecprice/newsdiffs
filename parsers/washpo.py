from baseparser import BaseParser
from bs4 import BeautifulSoup
import re
import datetime
import dateutil.parser

DATE_FORMAT = '%A, %B %e %Y, %l:%M %p'

class WashPoParser(BaseParser):
    SUFFIX = '?print=true'
    domains = ['www.washingtonpost.com']

    feeder_pat   = '^https?://www.washingtonpost.com/.*_story.html|https?://www.washingtonpost.com/.*/wp/.*/'
    feeder_pages = ['http://www.washingtonpost.com/']

    def _printableurl(self):
        return re.sub('_story.html.*', '_print.html', self.url)

    def _blog_parse(self, soup):
        elt = soup.find('h1', itemprop="headline")
        if elt is None:
            return False
        self.title = elt.getText().strip()

        elt = soup.find('span', itemprop='author')
        if elt is None:
            self.byline = ''
        else:
            self.byline = elt.getText().strip()

        elt = soup.find('span', itemprop="datePublished")
        if elt is None:
            self.date = ''
        else:
            datestr = elt['content']
            if datestr[-2:] == u'00' and datestr[-3] != u':':
                datestr = datestr[:-2] + u':00' # fix timezone formatting
            date = dateutil.parser.parse(datestr)
            self.date = date.strftime(DATE_FORMAT)
        div = soup.find('article', itemprop='articleBody')
        if div is None:
            return False
        self.body = '\n'+'\n\n'.join([x.getText().strip() for x in div.findAll('p')])
        return True

    def _parse(self, html):
        soup = BeautifulSoup(html)

        self.meta = soup.findAll('meta')
        elt = soup.find('h1', property="dc.title")
        if elt is None:
            if not self._blog_parse(soup):
                self.real_article = False
            return
        self.title = elt.getText().strip()
        elt = soup.find('h3', property="dc.creator")
        if elt is None:
            self.byline = ''
        else:
            self.byline = elt.getText().strip()

        elt = soup.find('span', datetitle="published")
        if elt is None:
            self.date = ''
        else:
            date = datetime.datetime.fromtimestamp(float(elt['epochtime'])/1000)
            self.date = date.strftime(DATE_FORMAT)

        div = soup.find('div', id='content')
        if div is None:
            self.real_article = False
            return
        self.body = '\n'+'\n\n'.join([x.getText().strip() for x in div.findAll('p')])
