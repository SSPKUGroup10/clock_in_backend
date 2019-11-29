# -*- coding:utf-8 -*-
from datetime import datetime
from app.extensions import db
from app.utils import generate_code_string, TIMESTAMP


class Audit(db.Model):
    __tablename__ = 'audit'

    @classmethod
    def make_audit_no(cls, audit_type):
        if audit_type == cls.AUDIT_TYPES['event']:
            audit_type = 'E'
        elif audit_type == cls.AUDIT_TYPES['group']:
            audit_type = 'G'

        return 'A{0}{1}-{2}'.format(
            audit_type,
            datetime.now().strftime(TIMESTAMP),
            generate_code_string(7, 'upper'))

    AUDIT_TYPES = {
        'event': 1,
        'group': 2
    }
    AUDIT_STATUS = {
        'committed': 1,
        'audited': 2,
        'canceled': -1,
        'rejected': -2,
        'forbid': -3
    }
    admin_id = db.Column(db.Integer, index=True)
    audit_number = db.Column(db.String(40))

    # 1: event 2: group
    audit_type = db.Column(db.Integer)
    business_uuid = db.Column(db.String(32))
    audit_title = db.Column(db.String(128))
    audit_time = db.Column(db.DateTime)
    # 1: committed 2: audited -1: cancelled -2: rejected -3: forbid
    status = db.Column(db.SmallInteger, default=1)
    audit_desc = db.Column(db.String(128))

    @property
    def audit_type_desc(self):
        if self.audit_type == 1:
            return '活动'
        elif self.audit_type == 2:
            return '社群'
        else:
            return '未知审核'

    @classmethod
    def create(cls, audit_type, business_uuid, audit_title):
        audit = cls()
        audit.audit_type = audit_type
        audit.business_uuid = business_uuid
        audit.audit_title = audit_title
        audit.audit_number = cls.make_audit_no(audit_type)
        db.session.add(audit)
        db.session.flush()
        return audit

    def audit_it(self, admin_id, audit_status, desc):
        if self.status == self.AUDIT_STATUS['committed'] and audit_status in self.AUDIT_STATUS.values():
            self.admin_id = admin_id
            self.status = audit_status
            self.audit_desc = desc
            db.session.add(self)
            db.session.commit()
            return True
        return False
