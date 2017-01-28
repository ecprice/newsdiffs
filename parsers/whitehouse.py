import datetime
import dateutil.parser

from baseparser import BaseParser
from BeautifulSoup import BeautifulSoup, Tag

DATE_FORMAT = '%A, %B %e %Y, %l:%M %p'

class WhitehouseParser(BaseParser):
    domains = ['www.whitehouse.gov']

    # TODO This pattern isn't finding most blog links. Why?
    feeder_pat   = '(^https://www.whitehouse.gov/)|(^/.*)'
    # All pages scraped from the root website as of Jan 27, 2017.
    feeder_pages = [
        'https://www.whitehouse.gov',
        'https://www.whitehouse.gov/1600/Presidents',
        'https://www.whitehouse.gov/1600/air-force-one',
        'https://www.whitehouse.gov/1600/camp-david',
        'https://www.whitehouse.gov/1600/constitution',
        'https://www.whitehouse.gov/1600/eeob',
        'https://www.whitehouse.gov/1600/elections-and-voting',
        'https://www.whitehouse.gov/1600/executive-branch',
        'https://www.whitehouse.gov/1600/federal-agencies-and-commissions',
        'https://www.whitehouse.gov/1600/first-ladies',
        'https://www.whitehouse.gov/1600/legislative-branch',
        'https://www.whitehouse.gov/1600/state-and-local-government',
        'https://www.whitehouse.gov/1600/vp-residence',
        'https://www.whitehouse.gov/administration/cabinet',
        'https://www.whitehouse.gov/administration/first-lady-melania-trump',
        'https://www.whitehouse.gov/administration/karen-pence',
        'https://www.whitehouse.gov/administration/president-trump',
        'https://www.whitehouse.gov/administration/vice-president-pence',
        'https://www.whitehouse.gov/america-first-energy',
        'https://www.whitehouse.gov/america-first-foreign-policy',
        'https://www.whitehouse.gov/blog',
        'https://www.whitehouse.gov/briefing-room/disclosures',
        'https://www.whitehouse.gov/briefing-room/legislation',
        'https://www.whitehouse.gov/briefing-room/nominations-and-appointments',
        'https://www.whitehouse.gov/briefing-room/presidential-actions',
        'https://www.whitehouse.gov/briefing-room/press-briefings',
        'https://www.whitehouse.gov/briefing-room/speeches-and-remarks',
        'https://www.whitehouse.gov/briefing-room/statements-administration-policy',
        'https://www.whitehouse.gov/briefing-room/statements-and-releases',
        'https://www.whitehouse.gov/bringing-back-jobs-and-growth',
        'https://www.whitehouse.gov/contact',
        'https://www.whitehouse.gov/copyright',
        'https://www.whitehouse.gov/law-enforcement-community',
        'https://www.whitehouse.gov/live/inauguration-45th-president-united-states',
        'https://www.whitehouse.gov/making-our-military-strong-again',
        'https://www.whitehouse.gov/participate/fellows',
        'https://www.whitehouse.gov/participate/internships',
        'https://www.whitehouse.gov/participate/tours-and-events',
        'https://www.whitehouse.gov/privacy',
        'https://www.whitehouse.gov/trade-deals-working-all-americans',
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
