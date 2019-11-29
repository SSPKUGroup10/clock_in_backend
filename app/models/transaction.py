# -*- coding:utf-8 -*-
from sqlalchemy.sql import func
from app.extensions import db



class Transaction(db.Model):
    __tablename = 'transaction'
    # Person to Yooqun(WeChat Pay) to Person
    TYPES = {
        # 站内余额转移会生成两笔流水，out -> in
        'in': 0,  # 收款人payee_id参与个人账户余额计算。数据来源：活动报名，付费会员，充值等
        'out': 1,  # 付款人payer_id参与个人账户余额的计算，数据来源：提现，退款等
    }
    #
    BUSINESS_TYPE = {
        'event': 0,  # 活动
        'group': 1,  # 社群
        'refund': 2,  # 退款
        'withdraw': 3,  # 提现
        'recharge': 4,  # 充值
        'migrate': 5,  # 迁移过来的费用
        'withdraw_fee': 6,  # 提现手续费
        'share_fee': 7,  # 活动分享奖励
        'share_fee_group': 8  #社群分享奖励
    }
    # 订单号
    order_no = db.Column(db.String(32), index=True)
    # 系统内交易（余额支付）id为NONE
    transaction_id = db.Column(db.String(32), unique=True, index=True)
    # 付款人
    payer_id = db.Column(db.Integer, index=True)
    # 收款人
    payee_id = db.Column(db.Integer, index=True)
    # 金额
    total_fee = db.Column(db.BigInteger, nullable=False)
    # 交易名称
    desc = db.Column(db.String(100))
    # 交易类型
    business_type = db.Column(db.SmallInteger)
    type = db.Column(db.SmallInteger)
    # 0 表示没有冻结, 1表示冻结, type为out的话表示已经支出, 不存在已经冻结的情况
    frozen = db.Column(db.Boolean)

    @classmethod
    def balance(cls, user_id):
        in_query = db.session.query(func.sum(cls.total_fee).label('total')) \
            .filter_by(payee_id=user_id, type=cls.TYPES['in'])
        available_in_query = in_query.filter_by(frozen=False)

        income_total = in_query.first().total or 0
        available_in_total = available_in_query.first().total or 0

        outcome_total = db.session.query(func.sum(cls.total_fee).label('total')) \
                            .filter_by(payer_id=user_id, type=cls.TYPES['out']) \
                            .first().total or 0

        available_total = (available_in_total - outcome_total) if available_in_total > outcome_total else 0
        total = (income_total - outcome_total) if income_total > outcome_total else 0
        return {
            'total': int(total),
            'availableTotal': int(available_total)
        }

    @classmethod
    def create_transaction(cls, payer_id, payee_id,
                           transaction_id, order_no,
                           total_fee, desc, business_type, income=True, frozen=True):
        transaction = cls()
        transaction.payer_id = payer_id
        transaction.payee_id = payee_id
        transaction.transaction_id = transaction_id
        transaction.total_fee = total_fee
        transaction.desc = desc
        transaction.business_type = Transaction.BUSINESS_TYPE[business_type]
        transaction.order_no = order_no
        if income:
            transaction.type = cls.TYPES['in']
            transaction.frozen = frozen
        else:
            transaction.type = cls.TYPES['out']
            transaction.frozen = False
        return transaction

    @property
    def business_type_desc(self):
        if self.business_type == 0:
            return 'event'
        if self.business_type == 1:
            return 'group'
        if self.business_type == 2:
            return 'refund'
        if self.business_type == 3:
            return 'withdraw'
        if self.business_type == 4:
            return 'recharge'
        if self.business_type == 5:
            return 'migrate'
        if self.business_type == 6:
            return 'withdrawee'
        if self.business_type == 7:
            return 'shareFee'
        if self.business_type == 8:
            return 'shareFeeGroup'



