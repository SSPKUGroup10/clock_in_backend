# -*- coding:utf-8 -*-
import os
from yaml import load as load_yml


class YmlEnv:
    def __init__(self, path):
        self.path = path

    def load_to_env(self):
        if os.path.exists(self.path):

            with open(self.path) as config_file:
                ret = load_yml(config_file)
                os.environ['FLASK_ENV'] = ret.get('FLASK_ENV') or 'development'
            return ret
        else:
            raise RuntimeError('Please complete your env.yml')

# config file must exit
env_config = YmlEnv('env/env.yml').load_to_env()

base_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig(object):
    SECRET_KEY = env_config.get('SECRET_KEY') or 'this is a very simple backend'

    SQLALCHEMY_DATABASE_URI = env_config.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join( base_dir , 'app.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False




class ProductionConfig(BaseConfig):
    DEBUG = False


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True


CONFIGS = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'testing': TestingConfig
}
