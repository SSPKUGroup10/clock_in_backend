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
    def get(self, id):
        return CircleItem().get(id)

    def put(self, id):
        data = request.get_json() or {}
        return CircleItem().update(id, data)

    def delete(self, id):
        return CircleItem().delete(id)
