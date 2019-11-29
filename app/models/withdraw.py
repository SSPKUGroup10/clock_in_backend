# -*- coding:utf-8 -*-
from datetime import datetime
from app.utils import TIMESTAMP, generate_code_string
from app.extensions import db


def make_order_no():
    return 'WD{0}{1}'.format(datetime.now().strftime(TIMESTAMP), generate_code_string(7, 'upper'))


class WithdrawOrder(db.Model):
    __tablename = 'withdraw_order'
    STATUS = {
        'committed': 1,
        'success': 2,
        'fail': -1,
        'refused': -2
    }
    desc = db.Column(db.String(200))

    order_number = db.Column(db.String(50), default=make_order_no, unique=True, index=True)
    transaction_id = db.Column(db.String(32), index=True)

    user_id = db.Column(db.Integer, index=True)
    amount = db.Column(db.Integer)
    charge_fee = db.Column(db.Integer)

    status = db.Column(db.SmallInteger, default=STATUS['committed'])
    refused_reason = db.Column(db.String(64))
    finished_time = db.Column(db.DateTime)

    @property
    def status_code(self):
        if self.status == WithdrawOrder.STATUS['committed']:
            return 'committed'
        elif self.status == WithdrawOrder.STATUS['success']:
            return 'success'
        elif self.status == WithdrawOrder.STATUS['refused']:
            return 'refused'
        else:
            return 'unknown'

    @classmethod
    def create(cls, user, amount, desc):
        withdraw = cls()
        withdraw.user_id = user.id
        withdraw.amount = amount
        withdraw.desc = desc
        db.session.add(withdraw)
        db.session.commit()
        return withdraw
