# -*- coding:utf-8 -*-
from importlib import import_module

from app.extensions.api import ApiNamespace
from .api import api

def add_resources(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/test', api)
    ns.add_resource(resources.TestResource, '/', strict_slashes=True)

    # 把resource 挂载上去
    api.init_app(app, **kwargs)


def init_module(app, **kwargs):
    add_resources(app, **kwargs)
