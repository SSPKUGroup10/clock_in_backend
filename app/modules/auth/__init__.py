# -*- coding:utf-8 -*-

from app.extensions.api import ApiNamespace

from ..api import api, auth_api


def init_module(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/auth', auth_api)
    ns.add_resource(resources.AuthRsc, '/login')
    ns.add_resource(resources.RegisterRsc, '/register')



