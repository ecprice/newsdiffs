from baseparser import BaseParser
import bs4

class TagesschauParser(BaseParser):
    SUFFIX = ''
    domains = ['www.tagesschau.de']

    def _parse(self, html):
        soup = bs4.BeautifulSoup(html)

        # extract the important text of the article into self.document #
        # select the one article
        article = soup.select('div.article')[0]
        # removing comments
        for x in self.descendants(article):
            if isinstance(x, bs4.Comment):
                x.extract()
        # removing elements which don't provide content
        for selector in ('.inv .teaserImg #seitenanfang .spacer .clearMe '+
            '.boxMoreLinks .metaBlock .weltatlas .fPlayer .zitatBox .flashaudio').split(' '):
            for x in article.select(selector):
                x.extract()
        # put hrefs into text form cause hrefs are important content
        for x in article.select('a'):
            x.append(" ["+x.get('href','')+"]")
        # ensure proper formating for later use of get_text()
        for x in article.select('li'):
            x.append("\n")
        for tag in 'p h1 h2 h3 h4 h5 ul div'.split(' '):
            for x in article.select(tag):
                x.append("\n\n")
        # strip multiple newlines away
        import re
        article = re.subn('\n\n+', '\n\n', article.get_text())[0]
        # important text is now extracted into self.document
        self.document = article

        self.title = soup.find('h1').get_text()

        # a by-line is not always there, but when it is, it is em-tag and
        # begins with the word 'Von'
        byline = soup.find('em')
        if byline:
            byline = byline.get_text()
            if 'Von ' not in byline: byline = None
        if not byline: byline = "nicht genannt"
        self.byline = byline

        # TODO self.date is unused, isn't it? but i still fill it here
        date = soup.select("div.standDatum")
        self.date = date and date[0].get_text() or ''

    # XXX a bug in bs4 that tag.descendants isnt working when .extract is called??
    # TODO investigate and report
    @staticmethod
    def descendants(tag):
        x = tag.next_element
        while x:
            next = x.next_element or x.parent and x.parent != tag and x.parent.next_sibling
            yield x
            x = next

    def __unicode__(self):
        return self.document
