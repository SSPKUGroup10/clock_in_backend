# -*- coding:utf-8 -*-
from flask import request
from flask_restful import Resource
from app.models import User
from app.modules.errors import ERRORS
from app.modules.auth import jwt


def jwt_auth_response(jwt_token, user):
    return {
        'accessToken': jwt_token.decode('utf-8'),
        'userInfo': user.username
    }


def user_login(kwargs):
    if not kwargs.get('username') or not kwargs.get('password'):
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg':  "用户账号密码为空"}
    user = User.query.filter_by(username=kwargs['username']).first()
    if user is None:
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg': '用户名或密码错误！'}
    if not user.verify_password(kwargs['password']):
        return {'status': 0, 'errCode': ERRORS['UserAuthError'][0], 'errMsg': '用户名或密码错误！'}

    jwt_token = jwt.encode({'uid': user.id})

    return {'status': 1, 'data': jwt_auth_response(jwt_token, user)}


class AuthRsc(Resource):
    def post(self):
        kwargs = request.get_json() or {}
        return user_login(kwargs)
