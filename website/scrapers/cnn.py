from . import *

class CNNArticle(Article):
    SUFFIX = ''
    domain = 'edition.cnn.com'
    fetcher_url = 'http://edition.cnn.com/'
    @staticmethod
    def article_url_filter(url): return 'edition.cnn.com/201' in url

    def _parse(self, html):
        from BeautifulSoup import BeautifulSoup
        from datetime import datetime, timedelta
        import re
        
        print 'got html'
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')
        print 'parsed'
        p_tags = soup.findAll('p', attrs={'class':re.compile(r'\bcnn_storypgraphtxt\b')})
        if not p_tags:
            self.real_article = False
            return

        self.meta = soup.findAll('meta')
        self.title = soup.find('meta', attrs={'itemprop':'headline'}).get('content')
        datestr = soup.find('meta', attrs={'itemprop':'dateModified'}).get('content')
        date = datetime.strptime(datestr, '%Y-%m-%dT%H:%M:%SZ') - timedelta(hours=4)
        self.date = date.strftime(DATE_FORMAT)
        self.byline = soup.find('meta', attrs={'itemprop':'author'}).get('content')
        lede = p_tags[0].previousSibling.previousSibling

        editornotes = soup.findAll('p', attrs={'class':'cnnEditorialNote'})
        contributors = soup.findAll('p', attrs={'class':'cnn_strycbftrtxt'})
        

        self.body = '\n'+'\n\n'.join([p.getText() for p in
                                      editornotes + [lede] + p_tags + contributors])
        authorids = soup.find('div', attrs={'class':'authorIdentification'})

    def __unicode__(self):
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))

