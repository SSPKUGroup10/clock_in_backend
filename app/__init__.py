# -*- coding:utf-8 -*-
import os
from flask import Flask
from config import CONFIGS


def init_app_in_debug_mode(app):
    if app.debug:
        pass


app = Flask(__name__)


def create_app(flask_config='development', **kwargs):
    config_name = os.getenv('FLASK_ENV', flask_config)
    app.config.from_object(CONFIGS[config_name])

    init_app_in_debug_mode(app)
    from . import models
    from . import extensions
    extensions.init_app(app)
    from . import modules
    from . import errorhandlers
    errorhandlers.init_app(app)
    modules.init_app(app)

    return app
