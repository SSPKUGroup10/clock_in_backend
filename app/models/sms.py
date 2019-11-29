# -*- coding:utf-8 -*-
from hashlib import md5
from app.extensions import db
from datetime import datetime, timedelta


class SmsRecord(db.Model):
    __tablename__ = 'sms_record'

    user_id = db.Column(db.Integer, index=True)

    business_type = db.Column(db.String(24), nullable=False)

    phone = db.Column(db.String(16), nullable=False)
    content = db.Column(db.String(256), nullable=False)
    result = db.Column(db.Integer, nullable=False)
    errmsg = db.Column(db.String(256))
    ext = db.Column(db.String(256))
    sid = db.Column(db.String(48))
    fee = db.Column(db.Integer, default=0)

    @classmethod
    def create(cls, **kwargs):
        return cls(**kwargs)


class SmsTemplate(db.Model):
    __tablename__ = 'sms_template'

    code = db.Column(db.String(24), nullable=False)
    name = db.Column(db.String(24), nullable=False)
    template_id = db.Column(db.Integer, nullable=False)

    @classmethod
    def create(cls, **kwargs):
        sms_template = cls(**kwargs)
        return db.save(sms_template)

    def update(self, **kwargs):
        if kwargs.get('code'):
            self.code = kwargs.get('code')
        if kwargs.get('name'):
            self.name = kwargs.get('name')
        if kwargs.get('template_id'):
            self.template_id = kwargs.get('template_id')
        return db.save(self)

    @classmethod
    def init_db(cls, items):
        for item in items:
            code = item[0]
            name = item[1]
            template_id = item[2]
            sms_template = cls.query.filter_by(code=code).first()
            if sms_template is None:
                sms_template = cls()
                sms_template.code = code
            sms_template.name = name
            sms_template.template_id = template_id
            db.session.add(sms_template)
        db.session.commit()


class SmsVerification(db.Model):
    __tablename__ = 'sms_verification'
    sms_record_id = db.Column(db.Integer)
    sid = db.Column(db.String(48))
    sign = db.Column(db.String(32))
    used = db.Column(db.Boolean, default=False)
    success_at = db.Column(db.DateTime)
    try_times = db.Column(db.SmallInteger, default=0)

    @classmethod
    def gen_sign(cls, key, phone, code, timestamp):
        origin = key
        origin += 'phone' + phone
        origin += 'verify_code' + code
        origin += 'timestamp' + timestamp
        origin += key
        sign = md5(bytearray(origin, 'utf_8')).hexdigest().upper()
        return sign

    @classmethod
    def get_by_sign(cls, sign):
        cls.filter_by(sign=sign, used=False).first()

    def verify(self, phone, code, timestamp, sign):
        now = datetime.now()
        success = False
        to_be_verified_sign = self.gen_sign(self.sid, phone, code, timestamp)
        if to_be_verified_sign == sign and self.sign == sign:
            if self.used is False:
                self.try_times += 1
                self.used = True
                if (now - timedelta(minutes=5)) <= self.created_at:
                    self.success_at = now
                    success = True
        else:
            self.try_times += 1
            if self.try_times == 5:
                self.used = True
        db.save(self)
        return success
