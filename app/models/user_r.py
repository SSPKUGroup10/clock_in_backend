# -*- coding:utf-8 -*-
import os

from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import datetime


class UserType(db.Model):
    __tablename__ = 'user_type'
    TYPES = {  # name  type_value charge_rate
        'normal': ['用户', 2],
        'seed': ['种子', 1],
        'golden_seed': ['金种子', 0]
    }

    type_key = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(24), unique=True)

    charge_rate = db.Column(db.Integer, default=2)

    @classmethod
    def init_db(cls):
        for type_key in cls.TYPES.keys():
            t = UserType.query.filter_by(type_key=type_key).first()
            if t is None:
                t = cls()
                t.type_key = type_key
            t.name = cls.TYPES[type_key][0]
            t.charge_rate = cls.TYPES[type_key][1]
            db.session.add(t)
            db.session.flush()
        db.session.commit()

    @classmethod
    def get_type(cls, type_key):
        return UserType.query.filter_by(type_key=type_key).first()


class User(db.Model):
    __tablename__ = 'user'
    group_id = db.Column(db.Integer, index=True)
    group_uuid = db.Column(db.String(32))
    user_type_id = db.Column(db.Integer, index=True)

    # 系统登录属性
    username = db.Column(db.String(32), unique=True)

    password_hash = db.Column(db.String(256))
    cell_phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(64), unique=True)

    # 用户基本属性
    fullname = db.Column(db.String(8), default='')
    # 1 male 2 female 0 unknown
    sex = db.Column(db.SmallInteger, default=0)
    birthday = db.Column(db.DateTime)
    quotes = db.Column(db.String(1000), default='')
    province = db.Column(db.String(16))
    province_id = db.Column(db.Integer)
    city = db.Column(db.String(64))
    city_id = db.Column(db.Integer)
    address = db.Column(db.String(64), default='')
    career = db.Column(db.String(526), default='')
    hobbies = db.Column(db.String(500), default='')
    activated = db.Column(db.Boolean, default=True)

    # 社交属性
    nickname = db.Column(db.String(64))
    avatar_url = db.Column(db.String(2048))
    user_wechat_id = db.Column(db.Integer)

    last_login_time = db.Column(db.DateTime, default=datetime.now)

    # 测试用
    is_fake = db.Column(db.Boolean, default=False)

    # 迁移用
    m_gender = db.Column(db.String(10), default="")
    m_openid = db.Column(db.String(32), default="")

    @property
    def has_phone(self):
        return True if self.cell_phone else False

    @property
    def phone(self):
        if self.cell_phone is None:
            return ''
        if len(self.cell_phone) == 11:
            return self.cell_phone[:3] + '******' + self.cell_phone[9:]
        else:
            return self.cell_phone[:3] + '********'

    @phone.setter
    def phone(self, phone):
        self.cell_phone = phone

    @property
    def password(self):
        return ''

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.username if self.username else self.id)


class UserLoginRecord(db.Model):
    __tablename__ = 'user_login_record'
    user_id = db.Column(db.Integer, index=True)
    login_time = db.Column(db.DateTime)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)

    ip = db.Column(db.String(64))
    user_agent = db.Column(db.String(512))

    ip_name = db.Column(db.String(128))
    device = db.Column(db.String(64))
    os = db.Column(db.String(128))
    os_version = db.Column(db.String(128))
    browser = db.Column(db.String(256))

    m_openid = db.Column(db.String(32))
    m_saledate = db.Column(db.Date)

    @classmethod
    def get_record(cls, session, user_id, year, month, day):
        return session.query(cls).filter_by(user_id=user_id, year=year, month=month, day=day).first()

    @classmethod
    def create_record(cls, session, user_id, ip, user_agent):
        login_time = datetime.now()
        record = cls.get_record(session, user_id, login_time.year, login_time.month, login_time.day)
        if record is None:
            record = cls()
            record.user_id = user_id
            record.login_time = login_time
            record.year = login_time.year
            record.month = login_time.month
            record.day = login_time.day
            record.ip = ip
            record.user_agent = user_agent
            session.add(record)
            session.commit()
        return record


class UserWechat(db.Model):
    __tablename__ = 'user_wechat'
    user_id = db.Column(db.Integer)

    public_openid = db.Column(db.String(32))
    scan_openid = db.Column(db.String(32))
    unionid = db.Column(db.String(32))
    subscribed = db.Column(db.Boolean, default=False)

    groupid = db.Column(db.Integer, default=0)
    sex = db.Column(db.SmallInteger, default=0)
    headimgurl = db.Column(db.String(2048))
    country = db.Column(db.String(24))
    province = db.Column(db.String(24))
    city = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    user_wechat_locations = db.relationship('UserWechatLocation', backref='user_wechat', lazy=True)


class UserWechatLocation(db.Model):
    __tablename__ = 'user_wechat_location'
    user_wechat_id = db.Column(db.Integer, db.ForeignKey('user_wechat.id'), nullable=False)

    longitude = db.Column(db.String(12))
    latitude = db.Column(db.String(12))
    precision = db.Column(db.String(12))


class UserGoldenSeedCert(db.Model):
    __tablename__ = 'user_goldenseed_cert'
    user_id = db.Column(db.Integer)
    user_wechat_id = db.Column(db.Integer)
    goldenseed_auth_url = db.Column(db.String(2048))


class UserShareHistory(db.Model):
    __table__name = 'user_share_history'
    user_id = db.Column(db.Integer)
    type_name = db.Column(db.String(12))  # 活动,社群
    type_uuid = db.Column(db.String(32))

    @classmethod
    def create_share_history(cls, share_user, type_name, type_uuid):
        share_history = cls()
        share_history.user_id = share_user.id
        share_history.type_name = type_name
        share_history.type_uuid = type_uuid
        db.session.add(share_history)
        db.session.commit()
        return share_history



