# -*- coding:utf-8 -*-
from flask_restful import Resource
from .decorator import response_json


class CommonResource(Resource):
    """
    这个类实现了返回结果被特殊处理过~，否则要自己手动格式化
    """
    method_decorators = [response_json()]
