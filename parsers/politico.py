from baseparser import BaseParser, grab_url, logger

# Different versions of BeautifulSoup have different properties.
# Some work with one site, some with another.
# This is BeautifulSoup 3.2.
from BeautifulSoup import BeautifulSoup
# This is BeautifulSoup 4
import bs4


class PoliticoParser(BaseParser):
    domains = ['www.politico.com']

    feeder_pat   = '^http://www.politico.com/(news/stories|story)/'
    feeder_pages = ['http://www.politico.com/']

    feeder_bs = bs4.BeautifulSoup

    def _parse(self, html):
        soup = bs4.BeautifulSoup(html)
        print_link = soup.findAll('a', text='Print')[0].get('href')
        html2 = grab_url(print_link)
        logger.debug('got html 2')
        # Now we have to switch back to bs3.  Hilarious.
        # and the labeled encoding is wrong, so force utf-8.
        soup = BeautifulSoup(html2, convertEntities=BeautifulSoup.HTML_ENTITIES,
                             fromEncoding='utf-8')

        self.meta = soup.findAll('meta')
        p_tags = soup.findAll('p')[1:]
        real_p_tags = [p for p in p_tags if
                       not p.findAll(attrs={'class':"twitter-follow-button"})]

        self.title = soup.find('strong').getText()
        entity = soup.find('span', attrs={'class':'author'})
        children = list(entity.childGenerator())
        try:
            self.byline = 'By ' + children[1].getText()
        except IndexError:
            self.byline = ''
        self.date = children[-1].strip()

        self.body = '\n'+'\n\n'.join([p.getText() for p in real_p_tags])
