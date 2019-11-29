# -*- coding:utf-8 -*-
from datetime import datetime
from app.utils import generate_code_string, TIMESTAMP, BusinessError
from app.models import SmsVerification
from .base import BaseQCloudSms


class QCloudSms(BaseQCloudSms):
    def _send_code(self, user_id, phone, template_code):
        if phone:
            now = datetime.now()
            code = generate_code_string(6, 'number')
            template = self.get_temp(template_code)
            if template:
                params = [code, 5]
                record = self.send_single_sms(user_id, phone, template.template_id, template_code, params)

                timestamp = now.strftime(TIMESTAMP)
                sms_verification = SmsVerification()
                sms_verification.sms_record_id = record.id
                sms_verification.sid = record.sid
                sms_verification.sign = SmsVerification.gen_sign(record.sid, phone, code, timestamp)
                sms_verification.timestamp = timestamp
                self.session.add(sms_verification)
                self.session.commit()
                return sms_verification
        raise BusinessError('Error', '没有电话', 400)

    def send_register_code(self, user_id, phone):
        return self._send_code(user_id, phone, 'register_code')

    def send_verify_code(self, user_id, phone):
        return self._send_code(user_id, phone, 'verify_code')

    def verify_sms_code(self, verification):
        sms_verification = self.session.query(SmsVerification).filter_by(sign=verification['sign']).get_first()
        if sms_verification is None:
            raise BusinessError('Error', '没有找到验证码', 404)
        verify = sms_verification.verify(verification['phone'], verification['code'],
                                         verification['timestamp'], verification['sign'])
        if verify is False:
            raise BusinessError('Error', '验证码错误', 60009)
