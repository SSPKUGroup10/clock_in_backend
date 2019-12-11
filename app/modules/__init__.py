# -*- coding:utf-8 -*-
from importlib import import_module


def init_app(app, **kwargs):
    modules = ['test', 'circle', 'auth', 'api'] # api must be the last one
    for module_name in modules:
        import_module('.%s' % module_name, package=__name__).init_module(app, **kwargs)
