# -*- coding:utf-8 -*-
from app.extensions.api import ApiNamespace
from ..api import api


def init_app(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/qcloud', api)
    ns.add_resource(resources.QCloudCOSResource, '/cos_sign')
