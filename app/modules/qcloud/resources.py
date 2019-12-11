# -*- coding:utf-8 -*-
from flask import request
from app.extensions import cos_sign
from app.utils import CommonResource


class QCloudCOSResource(CommonResource):
    def post(self):
        kwargs = request.get_json() or {}
        return cos_sign.get_authorization(kwargs)
