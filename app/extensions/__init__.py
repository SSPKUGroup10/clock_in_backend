# -*- coding:utf-8 -*-

from sqlalchemy.dialects.mysql import LONGTEXT
from .sqlalchemy_plus import SQLAlchemyPlus, CustomizedQuery, IdModel

from celery import Celery
from .flask_auth import JWTAuth

db = SQLAlchemyPlus(query_class=CustomizedQuery, model_class=IdModel)

LongText = LONGTEXT


def init_app(app):
    # for extension in [cross_origin_resource_sharing, db, cos_sign, wechat_config]:
    for extension in [db]: # 其他都暂时不要
        extension.init_app(app)
