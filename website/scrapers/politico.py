from . import *
import bs4

class PoliticoArticle(Article):
    domain = 'www.politico.com'
    fetcher_url = 'http://www.politico.com/'
    @staticmethod
    def article_url_filter(url): return 'www.politico.com/news/stories' in url
    find_article_urls_soup = bs4.BeautifulSoup

    def _parse(self, html):
        soup = bs4.BeautifulSoup(html)
        print_link = soup.findAll('a', text='Print')[0].get('href')
        html2 = grab_url(print_link)
        # Now we have to switch back to bs3.  Hilarious.
        # and the labeled encoding is wrong, so force utf-8.
        soup = BeautifulSoup(html2, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        p_tags = soup.findAll('p')[1:]

        self.title = soup.find('strong').getText()
        entity = soup.find('span', attrs={'class':'author'})
        children = list(entity.childGenerator())
        self.byline = 'By ' + children[1].getText()
        datestr = children[-1].strip()
        self.date = datestr

        self.body = '\n'+'\n\n'.join([p.getText() for p in p_tags])

    def __unicode__(self):
        return strip_whitespace(u'\n'.join((self.date, self.title, self.byline,
                                            self.body,)))

