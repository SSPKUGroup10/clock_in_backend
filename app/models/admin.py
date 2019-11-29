# -*- coding:utf-8 -*-
import csv
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import datetime


class Admin(db.Model):
    __tablename__ = 'admin'

    # 系统登录属性
    username = db.Column(db.String(32), unique=True)

    password_hash = db.Column(db.String(256))
    phone = db.Column(db.String(20), unique=True)
    email = db.Column(db.String(64), unique=True)

    # 用户基本属性
    fullname = db.Column(db.String(8), default='')

    activated = db.Column(db.Boolean, default=True)

    # 社交属性
    nickname = db.Column(db.String(64))
    avatar_url = db.Column(db.String(2048))

    last_login_time = db.Column(db.DateTime, default=datetime.now)
    login_histories = db.relationship('AdminLoginHistory', backref='admin', lazy=True)

    role_id = db.Column(db.Integer, index=True)
    permissions = db.Column(db.Integer)

    user_id = db.Column(db.Integer, index=True)
    openid = db.Column(db.String(32))

    @property
    def password(self):
        return ''

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Admin %r>' % self.username

    @classmethod
    def init_db(cls, admins):
        try:
            for ad in admins:
                username = ad[0]
                password = ad[1]
                phone = ad[2]
                email = ad[3]
                avatar_url = ad[4]
                nickname = ad[5]
                fullname = ad[6]
                role_name = ad[7]
                admin = Admin.query.filter_by(username=username).first()
                if admin is None:
                    admin = Admin()
                    admin.username = username
                role = AdminRole.query.filter_by(name=role_name).first()
                admin.password = password
                admin.phone = phone
                admin.email = email
                admin.avatar_url = avatar_url
                admin.nickname = nickname
                admin.fullname = fullname
                admin.role_id = role.id
                admin.permissions = role.permissions
                db.session.add(admin)
                db.session.flush()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class Permission:
    EVENT = 0x0001
    GROUP = 0x0002
    USER = 0x0004
    FINANCE = 0x0008
    SETTING = 0x0010
    AUDIT = 0x0020
    STATISTICS = 0x0040
    CMS = 0x0080
    STAFF = 0x0100
    CONFIG = 0x0200
    ALL = 0xFFFF


class AdminRole(db.Model):
    __tablename__ = 'admin_role'
    ROLES = {
        'EventAuditor': [Permission.EVENT, Permission.AUDIT],
        'GroupOperator': [Permission.GROUP, Permission.EVENT],
        'Accountant': [Permission.FINANCE],
        'PlatformOperator': [Permission.CMS, Permission.EVENT, Permission.GROUP],
        'Manager': [Permission.EVENT, Permission.GROUP, Permission.USER, Permission.AUDIT, Permission.STAFF],
        'IT': [Permission.SETTING],
        'DataMaintainer': [Permission.CONFIG],
        'SuperAdmin': [Permission.ALL]
    }

    DESCRIPTIONS = {
        'EventAuditor': '活动审核员',
        'GroupOperator': '社群运营',
        'Accountant': '财务',
        'PlatformOperator': '平台运营',
        'Manager': '经理',
        'IT': 'IT工程师',
        'DataMaintainer': '数据工程师',
        'SuperAdmin': '超级管理员'
    }
    name = db.Column(db.String(64), unique=True)
    desc = db.Column(db.String(64))
    permissions = db.Column(db.Integer)

    def has_permission(self, permission):
        return self.permissions & permission == permission

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permission(self):
        self.permissions = 0

    @classmethod
    def init_db(cls):
        for role_name in cls.ROLES.keys():
            role = db.session.query(cls).filter_by(name=role_name).first()
            if role is None:
                role = cls()
                role.name = role_name
            role.desc = cls.DESCRIPTIONS[role_name]
            role.reset_permission()
            for permission in cls.ROLES[role_name]:
                role.add_permission(permission)
            db.session.add(role)
        db.session.commit()


class AdminLoginHistory(db.Model):
    __tablename__ = 'admin_login_history'

    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False)

    ip = db.Column(db.String(64))
    ip_name = db.Column(db.String(128))
    user_agent = db.Column(db.String(512))
    device = db.Column(db.String(64))
    os = db.Column(db.String(128))
    os_version = db.Column(db.String(128))
    browser = db.Column(db.String(256))
    login_time = db.Column(db.DateTime)
