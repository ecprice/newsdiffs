from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag
import re
HEADLINE_PAT = re.compile(r'headline')


class GuardianParser(BaseParser):
    SUFFIX = '/print'
    domains = ['www.guardian.co.uk']

    feeder_pat = '^http://www.guardian.co.uk/[^/]+/201'
    feeder_pages = [
        'http://www.guardian.co.uk/',
    ]

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')

        title = soup.find('h1', itemprop=HEADLINE_PAT)
        if not title:
            self.real_article = False
            return
        self.title = title.getText()

        self.byline = ''
        byline = soup.find('div', 'contributor-full')
        if byline:
            self.byline = byline.getText().strip()

        self.date = ''
        date = soup.find('time', itemprop='datePublished')
        if date:
            self.date = date.getText()

        div = soup.find('div', id='article-body-blocks')
        if div is None:
            self.real_article = False
            return

        body = []

        # include subheadlines in body, as they often contain newsworthy
        # information themselves
        subhead = soup.find('p', id='stand-first')
        if subhead:
            body.extend(subhead.getText('\n').split('\n'))

        # strip out any <script> elements in story text (flash videos, etc.)
        [x.extract() for x in div.findAll('script')]

        body.extend([x.getText()
                     for x in div.recursiveChildGenerator()
                     if isinstance(x, Tag) and x.name in ('p', 'h2')])

        self.body = '\n'+'\n\n'.join(body)
