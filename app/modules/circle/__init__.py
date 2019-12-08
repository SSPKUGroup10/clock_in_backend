# -*- coding:utf-8 -*-
from importlib import import_module

from flask import Blueprint
from flask_restful import Api

from app.extensions.api import ApiNamespace
from app.modules.auth import jwt

api = Api()
blueprint = Blueprint('circles', __name__, url_prefix='/api/v1')


@blueprint.before_request  # blueprint 是要注册的~
@jwt.jwt_required()
def before_request():
    pass


def add_resources(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/circles', api)
    ns.add_resource(resources.CircleListRsc, '/', strict_slashes=True)
    ns.add_resource(resources.CircleItemRsc, '/<int:id>')
    ns.add_resource(resources.CircleMemRsc, '/<int:circle_id>/members/', strict_slashes=True)

    ######################################################
    # 这段能代码要写在最后，否则当前地址就无法挂到整个项目中去
    # 把resource 挂载上去
    # api.init_app(app, **kwargs)
    api.init_app(blueprint, **kwargs)
    app.register_blueprint(blueprint)


def init_module(app, **kwargs):
    add_resources(app, **kwargs)
