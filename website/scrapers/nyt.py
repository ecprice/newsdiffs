from . import *

# Parser for NYT articles
class NytArticle(Article):
    SUFFIX = '?pagewanted=all'
    domain = 'www.nytimes.com'
    fetcher_url = 'http://www.nytimes.com/'
    @staticmethod
    def article_url_filter(url): return 'www.nytimes.com/201' in url

    def _parse(self, html):
        from BeautifulSoup import BeautifulSoup
    
        soup = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        self.meta = soup.findAll('meta')
        self.seo_title = soup.find('meta', attrs={'name':'hdl'}).get('content')
        tmp = soup.find('meta', attrs={'name':'hdl_p'})
        if tmp and tmp.get('content'):
            self.title = tmp.get('content')
        else:
            self.title = self.seo_title
        self.date = soup.find('meta', attrs={'name':'dat'}).get('content')
        self.byline = soup.find('meta', attrs={'name':'byl'}).get('content')
        p_tags = soup.findAll('p', attrs={'itemprop':'articleBody'})
        self.body = '\n'.join([p.getText() for p in p_tags])
        authorids = soup.find('div', attrs={'class':'authorIdentification'})
        self.authorid = authorids.getText() if authorids else ''

        self.top_correction = '\n'.join(x.getText() for x in
                                   soup.findAll('nyt_correction_top')) or '\n'
        self.bottom_correction = '\n'.join(x.getText() for x in
                                   soup.findAll('nyt_correction_bottom')) or '\n'

    def __unicode__(self):
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
                                            self.top_correction, self.body,
                                            self.authorid,
                                            self.bottom_correction,)))
