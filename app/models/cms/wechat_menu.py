# -*- coding:utf-8 -*-
from app.extensions import db


class WechatMenu(db.Model):
    __tablename__ = 'wechat_menu'

    STATUS = {
        'committed': 0,  # 待上线
        'active': 1,  # 上线
        'offline': -1  # 已下线
    }

    TYPES = {
        'view': 0,  # 链接
        'click': 1,  # 点击
        'media_id': 2,  # 图文消息
        'location_select': 3,
    }
    # 菜单名称
    name = db.Column(db.String(128))
    # 菜单类型
    type = db.Column(db.String(36))
    # 菜单链接
    type_value = db.Column(db.String(1024))
    # 管理员id
    admin_id = db.Column(db.Integer, index=True)
    # 父级菜单id 0 为一级菜单
    parent_id = db.Column(db.Integer, index=True, default=0)
    sequence = db.Column(db.Integer, default=100)
    status = db.Column(db.Integer, default=STATUS['committed'])
    types = db.Column(db.Integer, default=TYPES['view'])

    @property
    def types_code(self):
        for key in self.TYPES.keys():
            if self.TYPES[key] == self.types:
                return key
        return 'unknown'

