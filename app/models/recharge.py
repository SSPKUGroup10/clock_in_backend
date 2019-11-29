# -*- coding:utf-8 -*-
from datetime import datetime
from werkzeug.exceptions import NotFound
from app.utils import TIMESTAMP, generate_code_string
from app.extensions import db
from app.models.user import User
from app.models.transaction import Transaction


def make_order_no():
    return 'RC{0}-{1}'.format(datetime.now().strftime(TIMESTAMP), generate_code_string(7, 'upper'))


class RechargeOrder(db.Model):
    STATUS = {
        'unpaid': 0,
        'paid': 1,
        'finished': 2,
        'canceled': -1,
        'system_canceled': -2
    }
    desc = db.Column(db.String(200))

    order_number = db.Column(db.String(50), default=make_order_no, unique=True, index=True)
    transaction_id = db.Column(db.Integer, index=True)

    user_id = db.Column(db.Integer, index=True)
    amount = db.Column(db.Integer)

    # 0: unpaid 1: paid -1: user canceled -2: system canceled
    status = db.Column(db.SmallInteger, default=STATUS['unpaid'])
    canceled_reason = db.Column(db.String(64))
    finished_time = db.Column(db.DateTime)

    expired_time = db.Column(db.DateTime)

    @property
    def status_code(self):
        if self.status == RechargeOrder.STATUS['unpaid']:
            return 'unpaid'
        elif self.status == RechargeOrder.STATUS['paid']:
            return 'paid'
        elif self.status == RechargeOrder.STATUS['finished']:
            return 'finished'
        elif self.status == RechargeOrder.STATUS['refunding']:
            return 'refunding'
        elif self.status == RechargeOrder.STATUS['refund']:
            return 'refund'
        elif self.status == RechargeOrder.STATUS['canceled']:
            return 'canceled'
        elif self.status == RechargeOrder.STATUS['system_canceled']:
            return 'system_canceled'
        else:
            return 'unknown'

    @classmethod
    def order_paid(cls, order_number, transaction_id):
        order = db.session.query(RechargeOrder).filter_by(order_number=order_number).first()
        if order is None:
            raise NotFound('Order not found')

        if order.status == RechargeOrder.STATUS['unpaid']:
            user = db.session.query(User).get(order.user_id)
            # create transaction
            transaction = Transaction.create_transaction(user.id, user.id,
                                                         transaction_id, order.order_number,
                                                         order.amount, order.desc, "recharge",
                                                         True, False)
            db.session.add(transaction)
            db.session.flush()
            # combine order with transaction
            order.transaction_id = transaction.id
            order.status = RechargeOrder.STATUS['finished']
            db.session.add(order)
            # commit all
            db.session.commit()
        return order
