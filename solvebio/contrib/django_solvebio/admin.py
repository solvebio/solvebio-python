from __future__ import absolute_import
from django.contrib import admin

from . import models


class DatasetAliasAdmin(admin.ModelAdmin):
    list_display = ['alias', 'dataset_id']
    search_fields = ['alias', 'dataset_id']

admin.site.register(models.DatasetAlias, DatasetAliasAdmin)
