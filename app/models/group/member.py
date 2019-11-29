# -*- coding:utf-8 -*-
from sqlalchemy import desc

from app.utils import monthdelta
from datetime import timedelta, date
from random import Random
from datetime import datetime
from app.extensions import db


class GroupMemberType(db.Model):
    __tablename__ = 'group_member_type'
    STATUS = {
        'draft': 0,
        'activated': 1,
        'deactivated': -1
    }
    UNIT_TYPES = {
        'daily': 0,
        'monthly': 1,
        'yearly': 2,
        'lifetime': 3
    }

    group_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(24))
    description = db.Column(db.String(1000), default='无')
    cover_url = db.Column(db.String(2048))
    status = db.Column(db.SmallInteger, default=STATUS['draft'])
    default = db.Column(db.Boolean, default=False)
    member_right_url = db.Column(db.String(2048))
    unit_type = db.Column(db.SmallInteger, default=UNIT_TYPES['monthly'])
    unit_price = db.Column(db.Integer, default=0)
    start_count = db.Column(db.Integer, default=1)
    count_step = db.Column(db.Integer, default=1)
    sequence = db.Column(db.Integer, default=1)
    
    share_award_rate = db.Column(db.Integer, default=0)

    # 迁移使用
    m_id = db.Column(db.Integer, default=0)
    m_amount = db.Column(db.Integer, default=0)
    m_group_id = db.Column(db.Integer, default=0)

    @property
    def status_code(self):
        for key in self.STATUS.keys():
            if self.STATUS[key] == self.status:
                return key
        return 'unknown'

    @property
    def unit_type_name(self):
        if self.unit_type == 0:
            return '天'
        elif self.unit_type == 1:
            return '月'
        elif self.unit_type == 2:
            return '年'
        elif self.unit_type == 3:
            return '终生'
        else:
            return '未知类型'

    def get_expected_daysdelta(self, the_day, unit_count):
        if self.unit_type == GroupMemberType.UNIT_TYPES['daily']:
            t = timedelta(days=unit_count)
        elif self.unit_type == GroupMemberType.UNIT_TYPES['monthly']:
            t = monthdelta(the_day, unit_count)
        elif self.unit_type == GroupMemberType.UNIT_TYPES['yearly']:
            t = monthdelta(the_day, unit_count * 12)
        else:
            t = timedelta(days=365 * 200)
        return t


class GroupMemberInfoTemplate(db.Model):
    __tablename__ = 'group_member_info_template'
    group_id = db.Column(db.Integer, index=True)

    name = db.Column(db.String(10))
    required = db.Column(db.Boolean, default=True)
    sequence = db.Column(db.Integer, default=100)


class GroupMemberInfo(db.Model):
    __tablename__ = 'group_member_info'
    group_member_id = db.Column(db.Integer)
    name = db.Column(db.String(10))
    value = db.Column(db.String(64))
    sequence = db.Column(db.Integer, default=100)


class GroupMember(db.Model):
    __tablename__ = 'group_member'

    STATUS = {
        'blocked': -2,  # 屏蔽
        'expired': -1,  # 过期
        'activated': 1  # 激活
    }

    group_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)

    nickname = db.Column(db.String(64))
    mark = db.Column(db.String(64))  # 备注
    packet = db.Column(db.String(64))  # 分组
    avatar_url = db.Column(db.String(2048))
    custom_desc = db.Column(db.String(512))

    card_number = db.Column(db.String(13), default=None)

    group_member_type_id = db.Column(db.Integer)
    first_join_at = db.Column(db.DateTime)
    start_at = db.Column(db.DateTime)
    expire_at = db.Column(db.DateTime)
    # -2: blocked -1: expired 1: activated
    status = db.Column(db.Integer, default=STATUS['activated'])
    m_id = db.Column(db.Integer)
    m_openid = db.Column(db.String(50))
    m_group_id = db.Column(db.Integer)
    m_group_member_type_id = db.Column(db.Integer)

    @property
    def expired(self):
        if self.expire_at:
            if datetime.now() <= self.expire_at:
                return False
        return True

    @property
    def valid_member(self):
        if self.status == self.STATUS['activated'] and not self.expired:
            return True
        return False

    @property
    def status_code(self):
        if self.status == self.STATUS['blocked']:
            return 'blocked'
        elif self.status == self.STATUS['expired']:
            return 'expired'
        elif self.status == self.STATUS['activated']:
            return 'activated'
        return 'unknown'

    def create_card_number(self):
        if self.card_number is None:
            year_month = datetime.now().strftime('%y%m%d')
            random_number = str(Random().randint(0, 9))
            count = GroupMember.query.filter_by(group_id=self.group_id).count()
            right_number = str(count).rjust(6, '0')
            self.card_number = year_month + random_number + right_number

    def create_card_number_ext(self):
        if self.card_number is None:
            year_month = self.created_at.strftime('%y%m%d')
            random_number = str(Random().randint(0, 9))
            count = GroupMember.query.filter_by(group_id=self.group_id).count()
            right_number = str(count).rjust(6, '0')
            self.card_number = year_month + random_number + right_number

    @classmethod
    def create_member(cls, group_id, record, user, custom_infos):
        member = db.session.query(GroupMember).filter_by(group_id=group_id, user_id=user.id).first()
        if member is None:
            member = cls()

            member.group_id = group_id
            member.user_id = user.id
            member.group_member_type_id = record.group_member_type_id

            member.nickname = user.nickname
            member.avatar_url = user.avatar_url

            member.first_join_at = record.start_at
            member.start_at = record.start_at
            member.expire_at = record.expire_at
            custom_data = ''
            count = 0
            for custom_info in custom_infos:
                custom_data += custom_info.get('name') + ':' + custom_info.get('value')
                if count != len(custom_infos) - 1:
                    custom_data += ','
                count = count + 1
            member.custom_desc = custom_data
            member.create_card_number()
        return member

    def flush_member(self, record):
        if self.expire_at < record.start_at:
            self.start_at = record.start_at
            self.expire_at = record.expire_at
            self.group_member_type_id = record.group_member_type_id
            if self.status == self.STATUS['expired']:
                self.status = self.STATUS['activated']


class GroupMemberRecord(db.Model):
    __tablename__ = 'group_member_record'
    STATUS = {
        'expired': -1,
        'paid': 0,
        'active': 1
    }
    group_id = db.Column(db.Integer, index=True)
    group_member_type_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)

    start_at = db.Column(db.DateTime)
    expire_at = db.Column(db.DateTime)
    status = db.Column(db.SmallInteger, default=STATUS['paid'])

    @classmethod
    def create_record(cls, group_id, member_type, user_id, unit_count, status=STATUS['paid']):
        start_day = cls.get_start_day(group_id, user_id)
        expire_day = start_day + member_type.get_expected_daysdelta(start_day, unit_count)
        record = cls()
        record.group_id = group_id
        record.group_member_type_id = member_type.id
        record.user_id = user_id
        record.start_at = start_day
        record.expire_at = expire_day
        record.status = status
        db.session.add(record)
        db.session.flush()
        return record

    @classmethod
    def get_start_day(cls, group_id, user_id):
        day = date.today()
        last_paid_record = db.session.query(cls) \
            .filter_by(group_id=group_id, user_id=user_id, status=cls.STATUS['paid']) \
            .order_by(desc(cls.expire_at)).first()
        if last_paid_record:
            day = last_paid_record.expire_at
        return day
