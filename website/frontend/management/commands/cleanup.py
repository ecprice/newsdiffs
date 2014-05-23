#!/usr/bin/python

import sys
import subprocess
import os
from frontend import models
from datetime import datetime, timedelta
import traceback
import time
import scraper

GIT_PROGRAM='git'

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--migrate',
            action='store_true',
            default=False,
            help='Recreate version + article database from git repo'),
        make_option('--remove-duplicates',
            action='store_true',
            default=False,
            help='Mark versions that appear multiple times in git repo as boring'),
        make_option('--mark-boring',
            action='store_true',
            default=False,
            help='Look through versions to mark boring ones'),
        )
    help = '''Modify versions in git repo

Articles that haven't changed in a while are skipped if we've
scanned them recently, unless --all is passed.
'''.strip()

    def handle(self, *args, **options):
        if options['migrate']:
            migrate_versions()
        if options['remove_duplicates']:
            remove_duplicates()
        if options['mark_boring']:
            mark_boring()


def migrate_versions():
    XXX_this_hasnt_been_updated_for_having_multiple_git_dirs
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

# Begin utility functions

# subprocess.check_output appeared in python 2.7.
# Linerva only has 2.6
def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    If the exit code was non-zero it raises a CalledProcessError.  The
    CalledProcessError object will have the return code in the returncode
    attribute and output in the output attribute.

    The arguments are the same as for the Popen constructor.  Example:

    >>> check_output(["ls", "-l", "/dev/null"])
    'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=STDOUT)
    'ls: non_existent_file: No such file or directory\n'
    """
    from subprocess import PIPE, CalledProcessError, Popen
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')
    process = Popen(stdout=PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        err = CalledProcessError(retcode, cmd)
        err.output = output
        raise err
    return output

if not hasattr(subprocess, 'check_output'):
    subprocess.check_output = check_output

def get_hash(version, filename):
    """Return the SHA1 hash of filename in a given version"""
    output = subprocess.check_output([GIT_PROGRAM, 'ls-tree', '-r',
                                      version, filename],
                                     cwd=models.GIT_DIR)
    return output.split()[2]

def remove_duplicates():
    num_articles = models.Article.objects.count()
    for i, article in enumerate(models.Article.objects.all()):
        if i%100 == 0:
            print '%s/%s' % (i+1, num_articles)
        filename = article.filename()
        mapping = {}
        versions = article.versions()
        if len(versions) <= 3:
            continue
        for v in versions:
            h = get_hash(v.v, filename)
            mapping[h] = mapping.get(h, 0) + 1
            if mapping[h] > 2:
                print article.url, 'should be boring', v.v, len(versions)
                v.boring = True
                v.save()

def mark_boring():
    articles = models.Article.objects.all()
    num_articles = articles.count()
    for i, article in list(enumerate(articles)):
        if i%100 == 0:
            print '%s/%s' % (i+1, num_articles)
        versions = list(article.versions())
        if len(versions) < 2:
            continue
        texts = [(v, v.text()) for v in versions]
        reload = False
        for v, text in texts:
            if text is None:
                #Inconsistency in database
                print 'ERROR: deleting', article.url, v.v
                v.delete()
                reload = True
        if reload:
            texts = [(v, v.text()) for v in versions if v.text()]

        for (old, oldtxt), (new, newtxt) in zip(texts, texts[1:]):
            if scraper.is_boring(oldtxt, newtxt):
                print 'Boring: %s %s %s' % (article.url, old.v, new.v)
                new.boring = True
                new.save()

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
    print >>sys.stderr, "Try `python website/manage.py cleanup`."
