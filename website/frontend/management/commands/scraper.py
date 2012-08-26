#!/usr/bin/python

import sys
import subprocess
import urllib2
import httplib
import os
from frontend import models
import re
from datetime import datetime, timedelta
import traceback

import diff_match_patch

# Different versions of BeautifulSoup have different properties.
# Some work with one site, some with another.
# This is BeautifulSoup 3.2.
from BeautifulSoup import BeautifulSoup, Tag
# This is BeautifulSoup 4
import bs4

import _monkeypatches
from _utils import *

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--migrate',
            action='store_true',
            default=False,
            help='Recreate version + article database from git repo'),
        make_option('--update',
            action='store_true',
            default=False,
            help='DEPRECATED; this is the default'),
        make_option('--all',
            action='store_true',
            default=False,
            help='Update _all_ stored articles'),
        make_option('--fetch',
            action='append',
            dest='fetch',
            help='Only fetch new articles from specific sites. '+
                 'If a scraper is available for a domain containing '+
                 'the argument to fetch, it will be used. Multiple '+
                 'use of this options adds up. Spaces split the '+
                 'argument in multiple usages of this option.'),
        )
    help = '''Scrape websites.

By default, scan front pages for new articles, and scan
existing and new articles to archive their current contents.

Articles that haven't changed in a while are skipped if we've
scanned them recently, unless --all is passed.
'''.strip()

    def handle(self, *args, **options):
        if options['migrate']:
            migrate_versions()
        else:
            print "load scrapers"
            load_scrapers(get_to_fetch(options['fetch']))
            print "update articles"
            update_articles()
            print "update versions"
            update_versions(options['all'])
        print "done"

def get_to_fetch(to_fetch):
    if not to_fetch:
        to_fetch = ['']
        print "fetch all"
    else:
        to_fetch = [x.split(' ') for x in to_fetch]
        to_fetch = set(filter(bool, sum(to_fetch, [])))
        print "fetch", ", ".join(to_fetch)
    return to_fetch

def migrate_versions():
    git_output = subprocess.check_output([GIT_PROGRAM, 'log'], cwd=models.GIT_DIR)
    commits = git_output.split('\n\ncommit ')
    commits[0] = commits[0][len('commit '):]
    print 'beginning loop'
    d = {}
    versions = [x.v for x in models.Version.objects.all()]
    for i, commit in enumerate(commits):
        (v, author, datestr, blank, changem) = commit.splitlines()
        if v in versions:
            continue
        fname = changem.split()[-1]
        changekind = changem.split()[0]
        if changekind == 'Reformat':
            continue
        date = datetime.strptime(' '.join(datestr.split()[1:-1]),
                                 '%a %b %d %H:%M:%S %Y')

        if not os.path.exists(os.path.join(models.GIT_DIR,fname)): #file introduced accidentally
            continue

        url = 'http://%s' % fname
        try:
            article = models.Article.objects.get(url=url)
        except models.Article.DoesNotExist:
            url += '/'
            try:
                article = models.Article.objects.get(url=url)
            except models.Article.DoesNotExist:
                url = url[:-1]
                article = models.Article(url=url,
                                         last_update=date,
                                         last_check=date)
                if not article.publication(): #blogs aren't actually reasonable
                    continue

                article.save()


        text = subprocess.check_output([GIT_PROGRAM, 'show',
                                        v+':'+fname],
                                       cwd=models.GIT_DIR)
        text = text.decode('utf-8')
        (date2, title, byline) = text.splitlines()[:3]

        boring = False

        print '%d/%d' % (i,len(commits)), url, v, date, title, byline, boring
        v = models.Version(article=article, v=v, date=date, title=title,
                           byline=byline, boring=boring)
        try:
            v.save()
        except models.IntegrityError:
            pass

###
domain_to_class = {} # used from get_scraper
url_fetchers = [] # used from get_all_article_urls

def load_scrapers(to_fetch):
    scrapers = get_scrapers()
    for scraper in scrapers:
        domain_to_class[scraper.domain] = scraper
        ###
        if any(p in scraper.domain for p in to_fetch):
            url_fetchers.append((scraper.fetcher_url, scraper.fetch_urls))

def get_scrapers():
    import os, importlib, scrapers
    pkg = 'scrapers'
    module_names = set(os.path.splitext(name)[0]
        for name in os.listdir(pkg))
    values = sum([importlib.import_module(pkg+'.'+name).__dict__.values()
        for name in module_names], [])
    scrapers = set(article
        for article in values
        if type(article) is type
        and article is not scrapers.Article
        and issubclass(article, scrapers.Article))
    return scrapers

def get_scraper(url):
    domain = url_to_filename(url).split('/')[0]
    return domain_to_class[domain]
### 

CHARSET_LIST = """EUC-JP GB2312 EUC-KR Big5 SHIFT_JIS windows-1252
IBM855
IBM866
ISO-8859-2
ISO-8859-5
ISO-8859-7
KOI8-R
MacCyrillic
TIS-620
windows-1250
windows-1251
windows-1253
windows-1255""".split()
def is_boring(old, new):
    oldu = old.decode('utf8')
    newu = new.decode('utf8')

    if oldu.splitlines()[1:] == newu.splitlines()[1:]:
        return True

    for charset in CHARSET_LIST:
        try:
            if oldu.encode(charset) == new:
                print 'Boring!'
                return True
        except UnicodeEncodeError:
            pass
    return False

def get_diff_info(old, new):
    dmp = diff_match_patch.diff_match_patch()
    dmp.Diff_Timeout = 3 # seconds; default of 1 is too little
    diff = dmp.diff_main(old, new)
    dmp.diff_cleanupSemantic(diff)
    chars_added   = sum(len(text) for (sign, text) in diff if sign == 1)
    chars_removed = sum(len(text) for (sign, text) in diff if sign == -1)
    return dict(chars_added=chars_added, chars_removed=chars_removed)

def add_to_git_repo(data, filename):
    full_path = os.path.join(models.GIT_DIR, filename)
    mkdir_p(os.path.dirname(full_path))

    boring = False
    diff_info = None
    already_exists = os.path.exists(full_path)
    if already_exists:
        previous = open(full_path).read()
        if previous == data:
            return None, None, None
        if is_boring(previous, data):
            boring = True
        else:
            diff_info = get_diff_info(previous, data)

    open(full_path, 'w').write(data)
    if not already_exists:
        subprocess.call([GIT_PROGRAM, 'add', filename], cwd=models.GIT_DIR)
        commit_message = 'Adding file %s' % filename
    else:
        commit_message = 'Change to %s' % filename
    subprocess.call([GIT_PROGRAM, 'commit', filename, '-m', commit_message],
                    cwd=models.GIT_DIR)
    v = subprocess.check_output([GIT_PROGRAM, 'rev-list', 'HEAD', '-n1', filename], cwd=models.GIT_DIR).strip()
    return v, boring, diff_info

#Update url in git
#Return whether it changed
def update_article(article):
    try:
        parser = get_scraper(article.url)
    except KeyError:
        print >> sys.stderr, 'Unable to parse domain, skipping'
        return
    try:
        parsed_article = parser(article.url)
        t = datetime.now()
    except (AttributeError, urllib2.HTTPError, httplib.HTTPException), e:
        if isinstance(e, urllib2.HTTPError) and e.msg == 'Gone':
            return
        print >> sys.stderr, 'Exception when parsing', article.url
        traceback.print_exc()
        print >> sys.stderr, 'Continuing'
        return
    if not parsed_article.real_article:
        return
    to_store = unicode(parsed_article).encode('utf8')
    v, boring, diff_info = add_to_git_repo(to_store, url_to_filename(article.url))
    if v:
        print 'Modifying! new blob: %s' % v
        v_row = models.Version(v=v,
                               boring=boring,
                               title=parsed_article.title,
                               byline=parsed_article.byline,
                               date=t,
                               article=article,
                               )
        v_row.diff_info = diff_info
        article.last_update = t
        v_row.save()
        article.save()

###
def fetch_urls():
    for url, fetch in url_fetchers:
        print "fetching", url, "...",
        sys.stdout.flush()
        urls = list(map(canonicalize_url, fetch()))
        print len(urls), "urls"
        if len(urls) is 0:
            print >> sys.stderr, "fetching of urls of {0} seams not to work".format(fetch.im_self)
        yield urls

def get_all_article_urls():
    return set(sum(fetch_urls(), []))

def update_articles():
    for url in get_all_article_urls():
        if not models.Article.objects.filter(url=url).count():
            models.Article(url=url).save()
###

def get_update_delay(minutes_since_update):
    days_since_update = minutes_since_update // (24 * 60)
    if minutes_since_update < 60*3:
        return 15
    elif days_since_update < 1:
        return 30
    elif days_since_update < 7:
        return 120
    elif days_since_update < 30:
        return 60*24
    else:
        return 60*24*7

def update_versions(do_all=False):
    articles = list(models.Article.objects.all())
    total_articles = len(articles)

    update_priority = lambda x: x.minutes_since_check() * 1. / get_update_delay(x.minutes_since_update())
    articles = sorted([a for a in articles if (update_priority(a) > 1 or do_all)], key=update_priority, reverse=True)

    print 'Checking %s of %s articles' % (len(articles), total_articles)
    for i, article in enumerate(articles):
        print 'Woo:', article.minutes_since_update(), article.minutes_since_check(), update_priority(article), '(%s/%s)' % (i+1, len(articles))
        delay = get_update_delay(article.minutes_since_update())
        if article.minutes_since_check() < delay and not do_all:
            continue
        print 'Considering', article.url, datetime.now()
        article.last_check = datetime.now()
        try:
            update_article(article)
        except Exception, e:
            print >> sys.stderr, 'Unknown exception when updating', article.url
            traceback.print_exc()
        article.save()
    subprocess.call([GIT_PROGRAM, 'gc'], cwd=models.GIT_DIR)
    print 'Done!'

legacy_bad_commit_range = (datetime(2012, 7, 8, 4, 0),
                           datetime(2012, 7, 8, 8, 0))
legacy_bad_commit_exceptions = """
828670ebb99e3422a203534b867c390f71d253d2
4681bf53fccbfd460b7b3e444f602f2e92f41ff0
795719cbee655c62f8554d79a89a999fd8ca5a9a
2acb2377130989bf7723bea283f1af146ae6ee6b
3955bf25ac01038cb49416292185857b717d2367
dda84ac629f96bfd4cb792dc4db1829e76ad94e5
64cfe3c10b03f9e854f2c24ed358f2cac4990e14
0ac04be3af54962dc7f8bb28550267543692ec28
2611043df5a4bfe28a050f474b1a96afbae2edb1
""".split()

if __name__ == '__main__':
    print >>sys.stderr, "Try `python website/manage.py scraper`."
