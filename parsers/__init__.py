#!/usr/bin/python

# To start tracking a new site:
#  - create a parser class in another file, based off (say) bbc.BBCParser
#  - add it to parsers (below)
# Test with test_parser.py

# List of parsers to import and use based on parser.domains

parsers = """
nyt.NYTParser
cnn.CNNParser
politico.PoliticoParser
bbc.BBCParser
washpo.WashPoParser
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

# Each feeder places URLs into the database to be checked periodically.

feeders = [parser.feed_urls for parser in parser_dict.values()]

__all__ = ['feeders', 'get_parser']
