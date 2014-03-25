from django.contrib import admin

from . import models


class DatasetAdmin(admin.ModelAdmin):
    list_display = ['alias', 'dataset_id']
    search_fields = ['alias', 'dataset_id']

admin.site.register(models.Dataset, DatasetAdmin)
