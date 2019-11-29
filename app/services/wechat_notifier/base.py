# -*- coding:utf-8 -*-
from app.models import WxNotifyTemplate

LINK_COLOR = '#173177'
NORMAL_COLOR = '#000000'
FAILED_COLOR = '#DC143C'
YOOQUN_COLOR = '#E75D29'


class WxTempNotifierBase:
    def __init__(self, session, wechat_service):
        self.session = session
        self.wechat_service = wechat_service

    def get_temp(self, code):
        return self.session.query(WxNotifyTemplate).filter_by(code=code).first()

    def send_notification(self, to_openid, template, data, url=None):
        try:
            self.wechat_service.message.send_template(to_openid, template.template_id, data, url)
        except Exception as e:
            print(e)
