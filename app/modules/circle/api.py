# -*- coding:utf-8 -*-
from flask import Blueprint
from flask_restful import Api


api = Api()
blueprint = Blueprint('circles', __name__, url_prefix='/circles')


def init_app(app, **kwargs):
    api.init_app(blueprint)
    app.register_blueprint(blueprint)




