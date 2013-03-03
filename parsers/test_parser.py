#!/usr/bin/python

import sys

try:
    parsername = sys.argv[1]
    url = sys.argv[2]
except IndexError:
    print 'Usage: test_parser.py <modulename>.<classname> <url_to_check>'
    sys.exit()

module, classname = parsername.rsplit('.', 1)
parser = getattr(__import__(module, globals(), fromlist=[classname]), classname)

parsed_article = parser(url)
print unicode(parsed_article)
