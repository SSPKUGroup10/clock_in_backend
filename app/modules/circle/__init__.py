# -*- coding:utf-8 -*-
from app.extensions.api import ApiNamespace

from ..api import api


def add_resources(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/circles', api)
    ns.add_resource(resources.CircleListRsc, '/', strict_slashes=True)
    ns.add_resource(resources.CircleItemRsc, '/<int:id>')
    ns.add_resource(resources.CircleMemRsc, '/<int:circle_id>/members/', strict_slashes=True)


def init_module(app, **kwargs):
    add_resources(app, **kwargs)
