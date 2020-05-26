# -*- coding: utf-8 -*-
from .apiresource import SingletonAPIResource


class User(SingletonAPIResource):
    RESOURCE = '/v1/user'
