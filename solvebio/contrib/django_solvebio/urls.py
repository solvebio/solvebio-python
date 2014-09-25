from __future__ import absolute_import
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^oauth2/token$',
        views.OAuth2AccessTokenView.as_view(), name="access-token"),
    url(r'^datasets/(?P<dataset>\w[\w\d\-\.\/]+)$',
        views.DatasetQueryView.as_view(), name="dataset-query"),
    url(r'^dashboards/(?P<dashboard>[-\w]+)$',
        views.DashboardView.as_view(), name="dashboard"),
)
