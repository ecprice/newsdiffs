from baseparser import BaseParser
import re
from BeautifulSoup import BeautifulSoup
from datetime import datetime, timedelta

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class CNNParser(BaseParser):
    domains = ['edition.cnn.com']

    feeder_pat   = '^http://edition.cnn.com/201'
    feeder_pages = ['http://edition.cnn.com/']

    def _parse(self, html):
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        p_tags = soup.findAll('p', attrs={'class':re.compile(r'\bcnn_storypgraphtxt\b')})
        if not p_tags:
            self.real_article = False
            return

        self.meta = soup.findAll('meta')
        self.title = soup.find('meta', attrs={'itemprop':'headline'}).get('content')
        datestr = soup.find('meta', attrs={'itemprop':'dateModified'}).get('content')
        if datestr:
            datet = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=4)
            self.date = datet.strftime(DATE_FORMAT)
        else:
            self.date = ''

        self.byline = soup.find('meta', attrs={'itemprop':'author'}).get('content')
        lede = p_tags[0].previousSibling.previousSibling

        editornotes = soup.findAll('p', attrs={'class':'cnnEditorialNote'})
        contributors = soup.findAll('p', attrs={'class':'cnn_strycbftrtxt'})

        self.body = '\n'+'\n\n'.join([p.getText() for p in
                                      editornotes + [lede] + p_tags + contributors])
