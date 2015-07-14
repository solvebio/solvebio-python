# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'DatasetAlias'
        db.create_table('django_solvebio_datasetalias', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('alias', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('dataset_id', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('django_solvebio', ['DatasetAlias'])


    def backwards(self, orm):
        # Deleting model 'DatasetAlias'
        db.delete_table('django_solvebio_datasetalias')


    models = {
        'django_solvebio.datasetalias': {
            'Meta': {'ordering': "['alias']", 'object_name': 'DatasetAlias'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'dataset_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['django_solvebio']
