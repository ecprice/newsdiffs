from django.db import models
import re
import subprocess
import os
from datetime import datetime

GIT_DIR = '/mit/ecprice/web_scripts/newsdiffs/articles'

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

_all_logs = {}

def _reset_metadata():
    global _all_logs
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
        if not os.path.exists(fname): #file introduced accidentally
            continue
        date = datetime.strptime(' '.join(datestr.split()[1:-1]),
                                 '%a %b %d %H:%M:%S %Y')
        d.setdefault(fname, []).append((date, v))
    _all_logs = d

# Create your models here.
class Article(models.Model):
    class Meta:
        db_table = 'articles'

    url = models.CharField(max_length=255, blank=False)

    def filename(self):
        return strip_prefix(self.url, 'http://').rstrip('/')

    def versions(self):
        vs = _all_logs.get(self.filename(), [])
        print vs
        return vs

    def get_version(self, version):
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
        return (date, title, byline)


def get_commit_date(commit):
    datestr = subprocess.check_output(['/usr/bin/git', 'show', '-s', '--format=%ci', commit], cwd=GIT_DIR)
    return datetime.strptime(datestr.strip(), '%Y-%m-%d %H:%M:%S -0400')
