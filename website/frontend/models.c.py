from django.db import models
import re
import subprocess
import os

GIT_DIR = '/mit/ecprice/web_scripts/newsdiffer/articles'

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

# Create your models here.
class Article(models.Model):
    class Meta:
        db_table = 'articles'

    url = models.CharField(max_length=255, blank=False)

    def filename(self):
        return strip_prefix(self.url, 'http://').rstrip('/')

    def versions(self):
        if not os.path.exists(GIT_DIR+'/'+self.filename()):
            return []
        output = subprocess.check_output(['/usr/bin/git', 'log',
                                          self.filename()], cwd=GIT_DIR)
        commits = [x.split()[1] for x in output.splitlines()
                   if x.startswith('commit')]
        dates = [' '.join(x.split()[1:]) for x in output.splitlines()
                 if x.startswith('Date:')]
        return zip(dates, commits)

    def get_version(self, version):
        return subprocess.check_output(['/usr/bin/git', 'show',
                                        version+':'+self.filename()],
                                       cwd=GIT_DIR)
