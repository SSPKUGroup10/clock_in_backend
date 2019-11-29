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


class BaseConfig(object):
    SECRET_KEY = env_config.get('SECRET_KEY') or 'this is a very simple backend'

    SQLALCHEMY_DATABASE_URI = env_config.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///' + os.path.join(os.getcwd() + 'app.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = env_config.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    # SQLALCHEMY_POOL_SIZE = env_config.get('SQLALCHEMY_POOL_SIZE', 100)
    # SQLALCHEMY_POOL_TIMEOUT = env_config.get('SQLALCHEMY_POOL_TIMEOUT', 5)
    # SQLALCHEMY_POOL_RECYCLE = 3600 * 6
    # SQLALCHEMY_ECHO = env_config.get('SQLALCHEMY_ECHO', False)
    # QCLOUD_SMS_APPID = env_config['QCloud']['sms']['app_id']
    # QCLOUD_SMS_APPKEY = env_config['QCloud']['sms']['app_key']
    #
    # COS_SECRET_ID = env_config['QCloud']['cos']['secret_id']
    # COS_SECRET_KEY = env_config['QCloud']['cos']['secret_key']
    # COS_HOST = env_config['QCloud']['cos']['host']
    # COS_BUCKET = env_config['QCloud']['cos']['bucket']
    # COS_REGION = env_config['QCloud']['cos']['region']
    #
    # WX_TOKEN = env_config['WeChat']['wx_token']
    # WX_APP_ID = env_config['WeChat']['wx_app_id']
    # WX_APP_SECRET = env_config['WeChat']['wx_app_secret']
    # WX_WEB_APP_ID = env_config['WeChat']['wx_web_app_id']
    # WX_WEB_APP_SECRET = env_config['WeChat']['wx_web_app_secret']
    #
    # WX_MCH_ID = env_config['WeChat']['wx_mch_id']
    # WX_MCH_KEY = env_config['WeChat']['wx_mch_key']
    # MOBILE_APP_URL = env_config['MobileUrl']['mobile_app_url']
    # PC_MANAGE_URL = env_config['MobileUrl']['pc_manage_url']
    # WX_CERT = 'cert/apiclient_cert.pem'
    # WX_CERT_KEY = 'cert/apiclient_key.pem'
    #
    # CELERY_BROKER_URL = 'redis://localhost:6379/0'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    #
    # APPLICATION = env_config['APPLICATION']


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
