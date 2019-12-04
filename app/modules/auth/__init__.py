# -*- coding:utf-8 -*-
from werkzeug.exceptions import NotFound
from flask import Blueprint
from flask_restful import Api

from app.extensions.api import ApiNamespace
from app.extensions.flask_auth import JWTAuth
from app.models import User


def jwt_identity(payload):
    user = User.query.get(payload['uid'])
    if user is None:
        raise NotFound('user not exist')
    return user


jwt = JWTAuth(get_identity_cb=jwt_identity)


api = Api()
blueprint = Blueprint('noAuth', __name__, url_prefix='/api/v1')

# login_required_url
auth_api = Api()
auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/v1')


@blueprint.before_request
@jwt.jwt_required()
def before_request():
    pass




def init_module(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/auth', auth_api)
    ns.add_resource(resources.AuthRsc, '/login')

    jwt.exp = 3600 * 2

    api.init_app(blueprint)
    app.register_blueprint(blueprint)

    auth_api.init_app(auth_blueprint)
    app.register_blueprint(auth_blueprint)
