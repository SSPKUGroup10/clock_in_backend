# -*- coding:utf-8 -*-
from flask import Blueprint
from flask_restful import Api
from .jwt import jwt

api = Api()
auth_api = Api()

blueprint = Blueprint('noAuth', __name__, url_prefix='/api/v1')
# login_required_url
auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1')


def init_module(app, **kwargs):
    api.init_app(blueprint)
    app.register_blueprint(blueprint)

    auth_api.init_app(auth_blueprint)
    app.register_blueprint(auth_blueprint)


@blueprint.before_request
@jwt.jwt_required()
def before_request():
    pass


