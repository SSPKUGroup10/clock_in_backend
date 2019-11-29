# -*- coding:utf-8 -*-
from app.extensions import db


class WxNotifyTemplate(db.Model):
    __tablename__ = 'wx_notify_template'

    code = db.Column(db.String(32), nullable=False)
    name = db.Column(db.String(32), nullable=False)
    template_id = db.Column(db.String(64), nullable=False)
    url_format = db.Column(db.String(2048))

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
