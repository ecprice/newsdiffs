#!/usr/bin/python

import BeautifulSoup
import bs4

# To start tracking a new site:
#  - create a parser class in another file, based off (say) bbc.BBCParser
#  - add it to parsers (below)
#  - add the homepage of the site to feeders (below)


# List of parsers to import and use based on parser.domains

parsers = """
nyt.NYTParser
cnn.CNNParser
politico.PoliticoParser
bbc.BBCParser
tagesschau.TagesschauParser
""".split()

parser_dict = {}

# Import the parsers and fill in parser_dict: domain -> parser
for parsername in parsers:
    module, classname = parsername.rsplit('.', 1)
    parser = getattr(__import__(module, globals(), fromlist=[classname]), classname)
    for domain in parser.domains:
        parser_dict[domain] = parser

def get_parser(url):
    return parser_dict[url.split('/')[2]]


# Determine which URLs get into the database to be checked periodically.

# The first entry is the homepage to look for urls
# The second entry is a filter on urls, returning True on urls to track
# The (optional) third entry is the BeautifulSoup version to use when
#  parsing the homepage.

feeders = [('http://www.nytimes.com/',
            lambda url: 'www.nytimes.com/201' in url),
           ('http://edition.cnn.com/',
            lambda url: 'edition.cnn.com/201' in url),
           ('http://www.politico.com/',
            lambda url: 'www.politico.com/news/stories' in url,
            bs4.BeautifulSoup),
           ('http://www.bbc.co.uk/news/',
            lambda url: 'www.bbc.co.uk/news' in url),
           ]

__all__ = ['feeders', 'get_parser']
