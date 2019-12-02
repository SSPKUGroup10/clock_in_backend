# -*- coding:utf-8 -*-
from importlib import import_module

from app.extensions.api import ApiNamespace
from .api import api


def add_resources(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/circles', api)
    ns.add_resource(resources.CircleListRsc, '/', strict_slashes=True)
    ns.add_resource(resources.CircleItemRsc, '/<int:id>/')

    # 把resource 挂载上去
    api.init_app(app, **kwargs)


def init_module(app, **kwargs):
    add_resources(app, **kwargs)
