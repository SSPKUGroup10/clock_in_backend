# -*- coding:utf-8 -*-
from qcloudsms_py import SmsSingleSender, SmsMultiSender
from app.models import SmsRecord, SmsTemplate
from app.utils import BusinessError


class BaseQCloudSms:
    def __init__(self):
        self.app_id = None
        self.app_key = None
        self._single_sender = None
        self._multi_sender = None
        self.session = None

    def __call__(self, app_id, app_key, session):
        self.app_id = app_id
        self.app_key = app_key
        self.session = session
        self._single_sender = SmsSingleSender(self.app_id, self.app_key)
        self._multi_sender = SmsMultiSender(self.app_id, self.app_key)

    def init_app(self, app):
        self.app_id = app.config['QCLOUD_SMS_APPID']
        self.app_key = app.config['QCLOUD_SMS_APPKEY']
        self._single_sender = SmsSingleSender(self.app_id, self.app_key)
        self._multi_sender = SmsMultiSender(self.app_id, self.app_key)

    @property
    def ssender(self):
        return self._single_sender

    @property
    def msender(self):
        return self._multi_sender

    def get_temp(self, code):
        return self.session.query(SmsTemplate).filter_by(code=code).first()

    def send_single_sms(self, user_id, phone, template_id, business_type, params):
        try:
            result = self.ssender.send_with_param(86, phone, template_id, params)
            record = SmsRecord.create(user_id=user_id, business_type=business_type, phone=phone, content=str(params),
                                      **result)
            self.session.add(record)
            self.session.commit()
            if record.result:
                raise BusinessError('QCloud Error', record.errmsg, record.result)
            return record
        except Exception as e:
            self.session.rollback()
            print(e)
            raise BusinessError('QCloud Error', 'Error', 500)
