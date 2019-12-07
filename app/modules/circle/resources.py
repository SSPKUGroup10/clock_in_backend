# -*- coding:utf-8 -*-
from flask import request
from flask import jsonify

from app.extensions.api import ApiNamespace
from app.utils import CommonResource

from .services import CircleList, CircleItem, CircleMember


class CircleListRsc(CommonResource):
    def get(self):
        return CircleList().get()

    def post(self):
        data = request.get_json() or {}
        ret_data = CircleList().create(**data)
        return ret_data


class CircleItemRsc(CommonResource):
    def get(self, id):
        """
        获取单个圈子的数据
        :param id:
        :return:
        """
        return CircleItem().get(id)

    def put(self, id):
        """
        修改圈子的数据
        :param id:
        :return:
        """
        data = request.get_json() or {}
        return CircleItem().update(id, data)

    def delete(self, id):
        """
        删除圈子
        :param id:
        :return:
        """
        return CircleItem().delete(id)


class CircleMemRsc(CommonResource):
    """
    圈子的成员资源
    """

    def get(self):
        """
        获取成员列表
        :return:
        """
        pass

    def post(self, circle_id):
        """
        加入圈子
        :return:
        """
        data = request.get_json() or {}
        return CircleMember(circle_id).join_circle(**data)