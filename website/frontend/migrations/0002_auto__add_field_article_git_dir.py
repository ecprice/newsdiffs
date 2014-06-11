# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Article.git_dir'
        db.add_column('Articles', 'git_dir',
                      self.gf('django.db.models.fields.CharField')(default='old', max_length=255),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Article.git_dir'
        db.delete_column('Articles', 'git_dir')


    models = {
        'frontend.article': {
            'Meta': {'object_name': 'Article', 'db_table': "'Articles'"},
            'git_dir': ('django.db.models.fields.CharField', [], {'default': "'old'", 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'last_check': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1901, 1, 1, 0, 0)'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(1901, 1, 1, 0, 0)'}),
            'url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'frontend.upvote': {
            'Meta': {'object_name': 'Upvote', 'db_table': "'upvotes'"},
            'article_id': ('django.db.models.fields.IntegerField', [], {}),
            'creation_time': ('django.db.models.fields.DateTimeField', [], {}),
            'diff_v1': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'diff_v2': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'upvoter_ip': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'frontend.version': {
            'Meta': {'object_name': 'Version', 'db_table': "'version'"},
            'article': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['frontend.Article']"}),
            'boring': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'byline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'diff_json': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'v': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        }
    }

    complete_apps = ['frontend']