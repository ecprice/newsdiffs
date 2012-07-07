from django.db import models
import re
import subprocess
import os
from datetime import datetime, timedelta

THIS_DIR = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(THIS_DIR))
GIT_DIR = ROOT_DIR+'/articles'

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

_all_logs = {}
_last_update = datetime.min

def _refresh_metadata(timeout=300):
    global _all_logs
    global _last_update

    timediff = (datetime.now() - _last_update)
    if timediff < timedelta(seconds=timeout):
        return
    git_output = subprocess.check_output(['/usr/bin/git', 'log'], cwd=GIT_DIR)
    commits = git_output.split('\n\ncommit ')
    commits[0] = commits[0][len('commit '):]
    d = {}
    for commit in commits:
        (v, author, datestr, blank, changem) = commit.splitlines()
        fname = changem.split()[-1]
        changekind = changem.split()[0]
        if changekind == 'Reformat':
            continue
        if not os.path.exists(os.path.join(GIT_DIR,fname)): #file introduced accidentally
            continue
        date = datetime.strptime(' '.join(datestr.split()[1:-1]),
                                 '%a %b %d %H:%M:%S %Y')
        d.setdefault(fname, []).append((date, v))
    for key in d:
        d[key].sort()
    _all_logs = d
    _last_update = datetime.now()

PublicationDict = {'www.nytimes.com': 'NYT',
                   'edition.cnn.com': 'CNN',
                   'www.politico.com': 'Politico',
                   }

# Create your models here.
class Article(models.Model):
    class Meta:
        db_table = 'Articles'

    url = models.CharField(max_length=255, blank=False, unique=True, db_index=True)

    def filename(self):
        return strip_prefix(self.url, 'http://').rstrip('/')

    def versions(self):
        _refresh_metadata(60*10)
        vs = _all_logs.get(self.filename(), [])
        print vs
        return vs

    def get_version(self, version):
        if version is None:
            return None
        return subprocess.check_output(['/usr/bin/git', 'show',
                                        version+':'+self.filename()],
                                       cwd=GIT_DIR)

    def latest_version(self):
        return open(GIT_DIR+'/'+self.filename()).read()

    def metadata(self):
        f = open(GIT_DIR+'/'+self.filename())
        date = f.readline().strip()
        title = f.readline().strip()
        byline = f.readline().strip()
        publication = PublicationDict.get(self.filename().split('/')[0])
        return dict(date=date, title=title, byline=byline, publication=publication)


class Upvote(models.Model):
    class Meta:
        db_table = 'upvotes'

    article_id = models.IntegerField(blank=False)
    diff_v1 = models.CharField(max_length=255, blank=False)
    diff_v2 = models.CharField(max_length=255, blank=False)
    creation_time = models.DateTimeField(blank=False)
    upvoter_ip = models.CharField(max_length=255)


def get_commit_date(commit):
    if commit is None:
        return datetime.now()
    datestr = subprocess.check_output(['/usr/bin/git', 'show', '-s', '--format=%ci', commit], cwd=GIT_DIR)
    return datetime.strptime(datestr.strip(), '%Y-%m-%d %H:%M:%S -0400')
