# -*- coding:utf-8 -*-
from app.extensions import db
from .._base import BaseUserAgent


# Group Show
class GroupShow(db.Model, BaseUserAgent):
    __tablename__ = 'group_show'

    STATUS = {
        'draft': 0,  # 草稿
        'published': 1,  # 发布
        'blocked': -2  # 屏蔽
    }

    group_id = db.Column(db.Integer, index=True)
    group_member_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)

    content = db.Column(db.String(200))
    images = db.relationship('GroupShowImage', backref='group_show', lazy=True)
    link_url = db.Column(db.String(2048))
    video_url = db.Column(db.String(2048))
    # -2: blocked 0: draft 1: published
    status = db.Column(db.Integer, default=0)
    on_top = db.Column(db.Boolean, default=False)
    sequence = db.Column(db.Integer, default=100)

    publish_at = db.Column(db.DateTime)

    like_count = db.Column(db.Integer, default=0)
    comment_count = db.Column(db.Integer, default=0)

    @property
    def status_code(self):
        for key in self.STATUS.keys():
            if self.STATUS[key] == self.status:
                return key
        return 'unknown'


class GroupShowImage(db.Model):
    __tablename__ = 'group_show_image'
    group_show_id = db.Column(db.Integer, db.ForeignKey('group_show.id'), nullable=False, index=True)
    image_url = db.Column(db.String(2048), nullable=False)
    sequence = db.Column(db.Integer, default=100)


class GroupShowComment(db.Model, BaseUserAgent):
    __tablename__ = 'group_show_comment'
    STATUS = {
        'published': 1,
        'blocked': -2
    }
    group_id = db.Column(db.Integer, index=True)
    group_show_id = db.Column(db.Integer, index=True)
    group_member_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)

    reply_to_member_id = db.Column(db.Integer, index=True)
    reply_to_user_id = db.Column(db.Integer, index=True)

    content = db.Column(db.String(100))
    img_comment_url = db.Column(db.String(2048))

    status = db.Column(db.SmallInteger, index=True, default=STATUS['published'])

    commentator_uuid = db.Column(db.String(32), nullable=False)
    commentator_nickname = db.Column(db.String(32))

    replyto_uuid = db.Column(db.String(32))
    replyto_nickname = db.Column(db.String(32))

    class Member:
        def __init__(self, uuid, nickname):
            self.uuid = uuid
            self.nickname = nickname

    @property
    def commentator(self):
        return GroupShowComment.Member(self.commentator_uuid, self.commentator_nickname)

    @commentator.setter
    def commentator(self, member):
        if member:
            self.group_id = member.group_id
            self.group_member_id = member.id
            self.user_id = member.user_id
            self.commentator_uuid = member.uuid
            self.commentator_nickname = member.nickname

    @property
    def reply_to_member(self):
        if self.replyto_uuid is None:
            return None
        return GroupShowComment.Member(self.replyto_uuid, self.replyto_nickname)

    @reply_to_member.setter
    def reply_to_member(self, member):
        if member:
            self.reply_to_member_id = member.id
            self.reply_to_user_id = member.user_id
            self.replyto_nickname = member.nickname
            self.replyto_uuid = member.uuid


class GroupShowLike(db.Model):
    __tablename__ = 'group_show_like'
    group_id = db.Column(db.Integer, index=True)
    group_show_id = db.Column(db.Integer, index=True)
    group_member_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)


class GroupShowView(db.Model):
    __tablename__ = 'group_show_view'
    group_show_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    member_id = db.Column(db.Integer, index=True)


class GroupShowViewStatistic(db.Model, BaseUserAgent):
    __tablename__ = 'group_show_statistic'
    group_show_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    member_id = db.Column(db.Integer, index=True)
    group_show_view_id = db.Column(db.Integer, index=True)
