# -*- coding:utf-8 -*-
from app.extensions import db
from app.utils import generate_code_string, CHARTYPES


def make_share_code():
    return generate_code_string(16, 'all')


class ShareAward(db.Model):
    __tablename__ = 'share_award'
    BUSINESS_TYPES = {
        'event': 0,
        'group': 1
    }
    share_user_id = db.Column(db.Integer, index=True)
    share_user_openid = db.Column(db.String(32))
    share_code = db.Column(db.String(16), default=make_share_code, unique=True, index=True)

    business_type = db.Column(db.SmallInteger, index=True)
    business_owner_id = db.Column(db.Integer, index=True)
    business_id = db.Column(db.Integer, index=True)

    award_rate = db.Column(db.Integer, default=10)

    @classmethod
    def create_share_award(cls, share_user, business_type, business_id, business_owner_id, award_rate=10):
        """
        :param share_user: 分享这个活动的人
        :param business_type: 分享的是活动还是社群
        :param business_id: 分享的活动的ID
        :param business_owner_id: 如果是活动,活动发布者
        :param award_rate: 奖励比例
        :return: 返回创建的分享奖励对象
        """
        if award_rate is None or award_rate <= 0:
            return None
        share_award = db.session.query(cls) \
            .filter_by(share_user_id=share_user.id, business_type=business_type, business_id=business_id) \
            .first()
        if share_award is None:
            share_award = cls()
            share_award.share_user_id = share_user.id
            share_award.share_user_openid = share_user.openid
            share_award.business_type = business_type
            share_award.business_id = business_id
            share_award.business_owner_id = business_owner_id
        share_award.award_rate = award_rate if award_rate < 100 else 10
        db.session.add(share_award)
        db.session.commit()
        return share_award


class ShareAwardRecord(db.Model):
    __tablename__ = 'share_award_record'
    RECORD_TYPES = {
        'view': 0,
        'order': 1
    }
    BUSINESS_TYPES = {
        'event': 0,
        'group': 1
    }
    STATUS = {
        'created': 0,
        'paid': 1,
        'finished': 2,
        'refund': -1
    }
    share_award_id = db.Column(db.Integer, index=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)   # 点击分享链接后报名的人
    order_id = db.Column(db.Integer, index=True)      # 点击分享链接报名创建的订单
    record_type = db.Column(db.SmallInteger)
    status = db.Column(db.SmallInteger, default=STATUS['created'])

    @classmethod
    def get_record(cls, share_code, record_type, business_type, user_id, order_id=None):
        if share_code is None:
            return None

        query = db.session.query(ShareAwardRecord.status.label('record_status'), ShareAwardRecord.id,
                                 ShareAward.business_type, ShareAward.business_id, ShareAward.business_owner_id,
                                 ShareAward.award_rate)
        query = query.join(ShareAward,
                           ShareAwardRecord.share_award_id == ShareAward.id)
        query = query.filter(ShareAwardRecord.record_type == record_type,
                             ShareAwardRecord.user_id == user_id,
                             ShareAward.share_code == share_code,
                             ShareAward.business_type == business_type, 
                             ShareAwardRecord.order_id == order_id)
        if query.first():
            share_award_record = ShareAwardRecord.query.get(query.first().id)
            return share_award_record
        else:
            return None

    @classmethod
    def create_record(cls, share_code, record_type, user_id, order_id=None):
        if share_code is None:
            return None

        share_award = db.session.query(ShareAward).filter_by(share_code=share_code).first()
        if share_award is None:
            return None

        record = db.session.query(ShareAwardRecord) \
            .filter_by(share_award_id=share_award.id, user_id=user_id, record_type=record_type, order_id=order_id) \
            .first()

        if record is None:
            record = cls()
            record.share_award_id = share_award.id
            record.user_id = user_id
            record.record_type = record_type
            record.order_id = order_id
            db.session.add(record)
            db.session.commit()
        return record

    def change_status(self, status):
        if self.record_type == self.RECORD_TYPES['order']:
            if self.status not in [self.STATUS['finished'], self.STATUS['refund']]:
                self.status = status
