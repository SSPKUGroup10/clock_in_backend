# -*- coding:utf-8 -*-
from datetime import datetime
from werkzeug.exceptions import NotFound
from app.utils import TIMESTAMP, generate_code_string
from app.extensions import db
from app.models.custom_type import CustomType
from app.models.user import User, UserWechat
from app.models.transaction import Transaction
from app.models.marketing.share_award import ShareAwardRecord, ShareAward
from .._base import BaseUserAgent
from .member import GroupMember, GroupMemberType, GroupMemberRecord


# Group
class Group(db.Model):
    __tablename__ = 'group'

    STATUS = {
        'draft': 0,
        'committed': 1,
        'audited': 2,
        'canceled': -1,
        'rejected': -2,
        'forbid': -3,
        'offline': -4
    }

    user_id = db.Column(db.Integer, index=True)
    group_type_id = db.Column(db.Integer, db.ForeignKey('group_type.id'), default=1)

    name = db.Column(db.String(512))
    logo_url = db.Column(db.String(2048))
    slogan = db.Column(db.String(64))
    brief_intro = db.Column(db.String(2048))
    detail_url = db.Column(db.String(2048))
    member_protocol_url = db.Column(db.String(2048))

    contact_phone = db.Column(db.String(20))
    founder_name = db.Column(db.String(64))

    tags = db.Column(db.String(36))
    status = db.Column(db.Integer, default=STATUS['draft'])

    found_at = db.Column(db.DateTime)

    on_top = db.Column(db.Boolean, default=False)
    sequence = db.Column(db.Integer, default=100)

    view_total = db.Column(db.Integer, default=0)
    info_update_year = db.Column(db.Integer, default=0)
    info_update_month = db.Column(db.Integer, default=0)
    info_update_day = db.Column(db.Integer, default=0)
    

    # 迁移用
    m_openid = db.Column(db.String(32), default="")
    m_id = db.Column(db.Integer, default=0)
    m_details = db.Column(db.Text, default="")

    @property
    def status_code(self):
        for key in self.STATUS.keys():
            if self.STATUS[key] == self.status:
                return key
        return 'unknown'

    @property
    def creator_openid(self):
        return UserWechat.query.filter_by(user_id=self.user_id).first().public_openid


class GroupView(db.Model):
    __tablename__ = 'group_view'
    group_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)


class GroupViewStatistic(db.Model, BaseUserAgent):
    __tablename__ = 'group_view_statistic'
    group_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    group_view_id = db.Column(db.Integer, index=True)


class GroupType(db.Model):
    __tablename__ = 'group_type'
    groups = db.relationship('Group', backref='group_type', lazy=True)
    name = db.Column(db.String(24))
    description = db.Column(db.String(64))

    GROUP_TYPES = [
        ['online', '线上社群'],
        ['offline', '线下社群']
    ]

    @classmethod
    def init_db(cls):
        for item in cls.GROUP_TYPES:
            name = item[0]
            description = item[1]
            group_type = cls.query.filter_by(name=name).first()
            if group_type is None:
                group_type = cls()
                group_type.name = name
                group_type.description = description
                db.session.add(group_type)
        db.session.commit()


class GroupMaterial(db.Model):
    __tablename__ = 'group_material'


class GroupTag(db.Model):
    __tablename__ = 'group_tag'
    group_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)
    sequence = db.Column(db.Integer, default=1000)


def make_order_no():
    return 'GM{0}-{1}'.format(datetime.now().strftime(TIMESTAMP),
                              generate_code_string(7, 'upper'))


class GroupOrder(db.Model):
    STATUS = {
        'unpaid': 0,
        'paid': 1,  # 付款完成
        'finished': 2,  # 订单完成了，不能在进行退款
        'canceled': -1,
        'system_canceled': -2
    }
    desc = db.Column(db.String(200))

    order_number = db.Column(db.String(50), default=make_order_no, unique=True, index=True)
    transaction_id = db.Column(db.Integer, index=True)

    group_id = db.Column(db.Integer, index=True)
    group_member_type_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)

    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    amount = db.Column(db.Integer)

    # 0: unpaid 1: paid -1: user canceled -2: system canceled
    status = db.Column(db.SmallInteger, default=STATUS['unpaid'])
    canceled_reason = db.Column(db.String(64))
    finished_time = db.Column(db.DateTime)
    expired_time = db.Column(db.DateTime)

    share_code = db.Column(db.String(16))

    m_id = db.Column(db.Integer)
    m_openid = db.Column(db.String(50))
    m_group_id = db.Column(db.Integer)
    m_group_member_type_id = db.Column(db.Integer)

    @property
    def status_code(self):
        if self.status == GroupOrder.STATUS['unpaid']:
            return 'unpaid'
        elif self.status == GroupOrder.STATUS['paid']:
            return 'paid'
        elif self.status == GroupOrder.STATUS['finished']:
            return 'finished'
        elif self.status == GroupOrder.STATUS['refunding']:
            return 'refunding'
        elif self.status == GroupOrder.STATUS['refund']:
            return 'refund'
        elif self.status == GroupOrder.STATUS['canceled']:
            return 'canceled'
        elif self.status == GroupOrder.STATUS['system_canceled']:
            return 'system_canceled'
        else:
            return 'unknown'

    @classmethod
    def order_paid(cls, order_number, transaction_id):
        order = db.session.query(GroupOrder).filter_by(order_number=order_number).first()
        if order is None:
            raise NotFound('Order not found')

        if order.status == GroupOrder.STATUS['unpaid']:
            user = db.session.query(User).get(order.user_id)
            group = db.session.query(Group).get(order.group_id)
            member_type = db.session.query(GroupMemberType).get(order.group_member_type_id)
            record = GroupMemberRecord.create_record(group.id, member_type, order.user_id, order.quantity)
            member = GroupMember.query.filter_by(group_id=order.group_id, user_id=order.user_id).first()
            new_member = False
            
            if member:
                member.flush_member(record)
            else:
                custom_infos = GroupUserCustomInfo.query.filter_by(user_id=user.id, group_id=group.id).all()
                custom_info_list = []
                if custom_infos:
                    for custom_info in custom_infos:
                        tmp_dict = {}
                        tmp_dict['name'] = custom_info.name
                        tmp_dict['value'] = custom_info.value
                        custom_info_list.append(tmp_dict)
                    
                member = GroupMember.create_member(group.id, record, user, custom_info_list)
                new_member = True
            db.session.add(member)
            db.session.flush()
            # create transaction
            transaction = Transaction.create_transaction(user.id, group.user_id,
                                                         transaction_id, order.order_number,
                                                         order.amount, order.desc, "group",
                                                         True, False)
            db.session.add(transaction)
            db.session.flush()
            # combine order with transaction
            order.transaction_id = transaction.id
            order.status = GroupOrder.STATUS['finished']
            order.new_member = new_member
            db.session.add(order)
            # commit all
            db.session.commit()
            
            record = ShareAwardRecord.get_record(order.share_code, ShareAwardRecord.RECORD_TYPES['order'],
                                                 ShareAwardRecord.BUSINESS_TYPES['group'],
                                                 order.user_id, order.id)
            if record:
                record.change_status(ShareAwardRecord.STATUS['finished'])
                db.session.add(record)
                db.session.commit()
                
                # 分享奖励
                share_award = ShareAward.query.filter_by(id=record.share_award_id).first()
                share_fee = order.amount * share_award.award_rate * 0.01
                transaction_in = Transaction.create_transaction(share_award.business_owner_id,
                                                                share_award.share_user_id,
                                                                None,
                                                                '{0}-{1}'.format("SH", order.order_number),
                                                                share_fee, group.name + ":分享奖励",
                                                                'share_fee_group',
                                                                True, False)
                transaction_out = Transaction.create_transaction(share_award.business_owner_id,
                                                                 share_award.share_user_id,
                                                                 None,
                                                                 '{0}-{1}'.format("SHO", order.order_number),
                                                                 share_fee, group.name + ":分享奖励支出",
                                                                 'share_fee_group',
                                                                 False, False)
                db.session.add(transaction_in)
                db.session.add(transaction_out)
                db.session.commit()
            
        return order, group, member


class GroupMemberRecruit(db.Model):
    __tablename__ = 'group_member_recruit'
    group_id = db.Column(db.Integer, index=True)

    playbill_url = db.Column(db.String(2048))
    agreement_url = db.Column(db.String(2048))
    recruit_doc = db.Column(db.String(1000))


class GroupCustomType(db.Model):
    __tablename__ = 'group_custom_type'
    
    group_id = db.Column(db.Integer, index=True)
    custom_type_uuid = db.Column(db.String(32))
    name = db.Column(db.String(32))
    sequence = db.Column(db.Integer, default=100)


class GroupUserCustomInfo(db.Model):
    __tabelname__ = 'group_user_custom_info'
    
    user_id = db.Column(db.Integer, index=True)
    group_id = db.Column(db.Integer, index=True)
    custom_info_uuid = db.Column(db.String(32))
    name = db.Column(db.String(32))
    value = db.Column(db.String(32))
    sequence = db.Column(db.Integer, default=100)
    
    @classmethod
    def create_user_custom(cls, group_id, user_id, custom_infos):
        if not custom_infos:
            return 
        
        for custom_info in custom_infos:
            custom_type = CustomType.query.filter_by( \
                    uuid=custom_info['custom_info_uuid']).first()
            user_custom_info = cls()
            user_custom_info.user_id = user_id
            user_custom_info.group_id = group_id
            user_custom_info.custom_info_uuid = custom_info['custom_info_uuid']
            user_custom_info.name = custom_info['name']
            user_custom_info.value = custom_info['value']
            user_custom_info.sequence = custom_type.sequence
            db.session.add(user_custom_info)
            
        db.session.commit()        
    