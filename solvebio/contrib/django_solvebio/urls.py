from __future__ import absolute_import
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^datasets/(?P<dataset>\w[\w\d\-\.\/]+)$',
        views.DatasetQueryView.as_view(), name="dataset-query"),
)
