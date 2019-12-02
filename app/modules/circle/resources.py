# -*- coding:utf-8 -*-
from flask import request
from flask import jsonify

from app.extensions.api import ApiNamespace
from app.utils import CommonResource

from .services import CircleList, CircleItem


class CircleListRsc(CommonResource):
    def get(self):
        return CircleList().get()

    def post(self):
        data = request.get_json() or {}
        ret_data = CircleList().create(**data)
        return ret_data


class CircleItemRsc(CommonResource):
    def get(self):
        pass

    def put(self):
        pass
