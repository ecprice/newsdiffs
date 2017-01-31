from datetime import datetime

import json
import hashlib
from django.db import models

def strip_prefix(string, prefix):
    if string.startswith(prefix):
        string = string[len(prefix):]
    return string

PublicationDict = {'www.nytimes.com': 'NYT',
                   'edition.cnn.com': 'CNN',
                   'www.bbc.co.uk': 'BBC',
                   'www.politico.com': 'Politico',
                   'www.washingtonpost.com': 'Washington Post',
                   'whitehouse.gov': 'The White House',
                   }

ancient = datetime(1901, 1, 1)

# Create your models here.
class Article(models.Model):
    class Meta:
        db_table = 'Articles'

    url = models.CharField(max_length=255, blank=False, unique=True,
                           db_index=True)
    initial_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(default=ancient)
    last_check = models.DateTimeField(default=ancient)

    def filename(self):
        ans = self.url.rstrip('/')
        if ans.startswith('http://'):
            return ans[len('http://'):]
        elif ans.startswith('https://'):
            # Terrible hack for backwards compatibility from when https was stored incorrectly,
            # perpetuating the problem
            return 'https:/' + ans[len('https://'):]
        raise ValueError("Unknown file type '%s'" % self.url)

    def publication(self):
        return PublicationDict.get(self.url.split('/')[2])

    def versions(self):
        return self.version_set.filter(boring=False).order_by('date')

    def latest_version(self):
        return self.versions().latest()

    def first_version(self):
        return self.versions()[0]

    def minutes_since_update(self):
        delta = datetime.now() - max(self.last_update, self.initial_date)
        return delta.seconds // 60 + 24*60*delta.days

    def minutes_since_check(self):
        delta = datetime.now() - self.last_check
        return delta.seconds // 60 + 24*60*delta.days

class TextBlob(models.Model):
    """Stores a text blob, most often an article body, indexed by SHA-1 hash."""
    class Meta:
        db_table: 'text_blob'

    # Use a Sha256 content hash.
    key = models.CharField(max_length=64, primary_key=True)
    blob = models.TextField()

    @classmethod
    def create_or_get(cls, text_to_insert):
        content_hash = hashlib.sha256(text_to_insert)
        result = cls.objects.filter(key=content_hash)
        if len(result) == 0:
            return cls(key=content_hash, blob=text_to_insert)
        return result[0]


class Version(models.Model):
    class Meta:
        db_table = 'version'
        get_latest_by = 'date'

    article = models.ForeignKey(Article, null=False)
    title = models.CharField(max_length=255, blank=False)
    byline = models.CharField(max_length=255,blank=False)
    date = models.DateTimeField(db_index=True, blank=False)
    boring = models.BooleanField(blank=False, default=False)
    diff_json = models.CharField(max_length=255, null=True)
    text = models.ForeignKey(TextBlob, null=False)

    def get_diff_info(self):
        if self.diff_json is None:
            return {}
        return json.loads(self.diff_json)
    def set_diff_info(self, val=None):
        if val is None:
            self.diff_json = None
        else:
            self.diff_json = json.dumps(val)
    diff_info = property(get_diff_info, set_diff_info)


class Upvote(models.Model):
    class Meta:
        db_table = 'upvotes'

    article_id = models.IntegerField(blank=False)
    diff_v1 = models.CharField(max_length=255, blank=False)
    diff_v2 = models.CharField(max_length=255, blank=False)
    creation_time = models.DateTimeField(blank=False)
    upvoter_ip = models.CharField(max_length=255)
