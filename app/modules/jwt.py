# -*- coding:utf-8 -*-

from werkzeug.exceptions import NotFound

from app.extensions.flask_auth import JWTAuth
from app.models.user import User


def jwt_identity(payload):
    user = User.query.get(payload['uid'])
    if user is None:
        raise NotFound('user not exist')
    return user


jwt = JWTAuth(get_identity_cb=jwt_identity)
jwt.exp = 3600 * 2