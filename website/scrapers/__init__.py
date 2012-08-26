from frontend.management.commands._utils import *

DATE_FORMAT = '%B %d, %Y at %l:%M%P EDT'

class Article(object):
    SUFFIX = ''
    domain = ''

    def __init__(self, url):
        self.url = url
        self.real_article = True
        self.html = grab_url(url + self.SUFFIX)
        self._parse(self.html)

