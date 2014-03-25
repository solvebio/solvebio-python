# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Dataset'
        db.create_table(u'django_solvebio_dataset', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('dataset_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'django_solvebio', ['Dataset'])


    def backwards(self, orm):
        # Deleting model 'Dataset'
        db.delete_table(u'django_solvebio_dataset')


    models = {
        u'django_solvebio.dataset': {
            'Meta': {'object_name': 'Dataset'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'dataset_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['django_solvebio']