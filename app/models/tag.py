# -*- coding:utf-8 -*-
from sqlalchemy import and_

from app.extensions import db


class Tag(db.Model):
    __tablename__ = 'tag'
    name = db.Column(db.String(10), unique=True)
    user_id = db.Column(db.Integer, index=True)
    admin_id = db.Column(db.Integer, index=True)
    reference_count = db.Column(db.Integer, default=0)
    sequence = db.Column(db.Integer, default=100)

    def _auto_reference(self, cls, business_type, business_id):
        try:
            auto_reference = db.session.query(cls).filter(and_(cls.tag_id == self.id,
                                                               cls.business_type == business_type,
                                                               cls.business_id == business_id)).first()
            if auto_reference:
                return

            auto_reference = cls()
            auto_reference.tag_id = self.id
            auto_reference.business_type = business_type
            auto_reference.business_id = business_id
            db.session.add(auto_reference)
            db.session.flush()

            reference_count = TagReference.query.filter_by(tag_id=self.id).count()
            unreference_count = TagUnreference.query.filter_by(tag_id=self.id).count()
            self.reference_count = reference_count - unreference_count
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def reference(self, business_type, business_id):
        return self._auto_reference(TagReference, business_type, business_id)

    def un_reference(self, business_type, business_id):
        return self._auto_reference(TagUnreference, business_type, business_id)


class ReferenceMixin:
    tag_id = db.Column(db.Integer)
    business_id = db.Column(db.Integer)
    business_type = db.Column(db.Integer)

    @property
    def business_name(self):
        if self.business_type == 1:
            return '活动'
        elif self.business_type == 2:
            return '社群'
        return '未知类型'


class TagReference(db.Model, ReferenceMixin):
    __tablename__ = 'tag_reference'


class TagUnreference(db.Model, ReferenceMixin):
    __tablename__ = 'tag_unreference'


class PersonTypeTag(db.Model):
    """
    每个用户定义的分组
    """
    __tablename__ = 'person_type_tag'
    creator_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(32), index=True)
    desc = db.Column(db.String(200))


class PersonTag(db.Model):
    """
    每个用户对某一个其他用户的标签, 一个用户可以对其他用户打多个标签
    """
    __tablename__ = 'person_tag'
    tag_id = db.Column(db.Integer, index=True)
    person_id = db.Column(db.Integer, index=True)
    delete = db.Column(db.Integer, default=0)


class PersonRemark(db.Model):
    __tablename__ = 'person_remark'
    """
    某个用户对其他另一个用户的备注, 只能有一个
    """
    mark_from_id = db.Column(db.Integer, index=True)
    mark_to_id = db.Column(db.Integer, index=True)
    mark = db.Column(db.String(200))
