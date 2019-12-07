# -*- coding:utf-8 -*-
from flask import request
from flask_restful import Resource
from .services import user_login, register


def jwt_auth_response(jwt_token, user):
    return {
        'accessToken': jwt_token.decode('utf-8'),
        'userInfo': user.username
    }


class AuthRsc(Resource):
    def post(self):
        kwargs = request.get_json() or {}
        return user_login(kwargs)


class RegisterRsc(Resource):
    def post(self):
        kwargs = request.get_json() or {}
        return register(kwargs)