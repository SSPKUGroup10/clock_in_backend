# -*- coding:utf-8 -*-
from importlib import import_module
from flask import Blueprint


from app.extensions.api import ApiNamespace
from app.extensions.flask_auth import JWTAuth


from .api import api


def jwt_identity(payload):
    from app.models.user import User
    from werkzeug.exceptions import NotFound
    user = User.query.get(payload['uid'])
    if user is None:
        raise NotFound('user not exist')
    return user


jwt = JWTAuth(get_identity_cb=jwt_identity)

blueprint = Blueprint("test", __name__, url_prefix="/api/v1")


@blueprint.before_request
@jwt.jwt_required()
def before_request():
    pass


def add_resources(app, **kwargs):
    from . import resources
    ns = ApiNamespace('/test', api)
    ns.add_resource(resources.TestResource, '/', strict_slashes=True)
    ns.add_resource(resources.TestModelRsc, '/model/')

    # 把resource 挂载上去
    api.init_app(blueprint)
    app.register_blueprint(blueprint)




def init_module(app, **kwargs):
    add_resources(app, **kwargs)
