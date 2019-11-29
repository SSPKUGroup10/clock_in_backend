# -*- coding:utf-8 -*-
from redis import Redis
from wechatpy.client import WeChatClient
from wechatpy.session.redisstorage import RedisStorage


class BaseWeChatService:
    def __init__(self, wx_app_id, wx_app_secret, redis_url='redis://127.0.0.1:6379/0', prefix='wechat_py'):
        redis_client = Redis.from_url(redis_url)
        session_interface = RedisStorage(redis_client, prefix)
        self.appid = wx_app_id
        self.wechat_client = WeChatClient(wx_app_id, wx_app_secret, session=session_interface)

    @property
    def jsapi(self):
        return self.wechat_client.jsapi

    @property
    def message(self):
        return self.wechat_client.message
