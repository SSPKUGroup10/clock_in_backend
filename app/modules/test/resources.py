# -*- coding:utf-8 -*-
from flask import request
from flask import jsonify

from app.extensions.api import ApiNamespace
from app.utils import CommonResource

from .services import TestObj, TestModelEntity


class TestResource(CommonResource):
    def get(self):
        return TestObj().get()

    def post(self):
        data = request.get_json() or {}
        data['recieve'] = 1
        return data


class TestModelRsc(CommonResource):
    def post(self):
        data = request.get_json() or {}
        ret_data = TestModelEntity().create(**data)
        return ret_data