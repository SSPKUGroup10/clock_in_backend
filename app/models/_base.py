# -*- coding:utf-8 -*-
from app.extensions import db


class BaseTransaction(db.Model):
    __abstract__ = True
    STATUS = {
        'created': 0,
        'success': 1,
        'failed': -1
    }
    transaction_number = db.Column(db.String(128))
    wechat_transaction_no = db.Column(db.String(128))

    # 付款人
    payer_id = db.Column(db.Integer, index=True)
    payer_name = db.Column(db.String(64))
    # 收款人
    payee_id = db.Column(db.Integer, index=True)
    payee_name = db.Column(db.String(64))
    amount = db.Column(db.Integer)

    # 交易名称
    transaction_name = db.Column(db.String(64))
    # 0: payment 1: refund
    transaction_type = db.Column(db.Integer, default=0)

    finished_time = db.Column(db.DateTime)
    # 0: created 1: success -1: failed
    status = db.Column(db.SmallInteger)
    status_code = db.Column(db.Integer)


class BaseUserAgent:
    ip = db.Column(db.String(64))
    ip_name = db.Column(db.String(128))
    user_agent = db.Column(db.String(512))
    device = db.Column(db.String(64))
    os = db.Column(db.String(128))
    os_version = db.Column(db.String(128))
    browser = db.Column(db.String(256))


class BasePublish:
    published = db.Column(db.Boolean, default=True)
    sequence = db.Column(db.Integer, default=100)
