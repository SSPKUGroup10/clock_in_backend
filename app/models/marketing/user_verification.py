from app.extensions import db


class UserVerificationRecord(db.Model):
    __tablename__ = 'user_verification_record'

    STATUS = {
        'draft': 0,
        'committed': 1,
        'approved': 2,
        'reject': -1
    }

    user_id = db.Column(db.Integer, index=True)

    wechat_number = db.Column(db.String(32))
    career = db.Column(db.String(32))
    interested_event = db.Column(db.String(128))
    best_joined_group = db.Column(db.String(128))
    most_expected_func = db.Column(db.String(128))

    wechat_media_id = db.Column(db.String(1024))
    verify_image_url = db.Column(db.String(2048))

    status = db.Column(db.Integer, default=STATUS['draft'])

    @classmethod
    def create_verify_record(cls, user, params):
        record = UserVerificationRecord.query.filter(UserVerificationRecord.user_id == user.id).first()
        if record is None:
            record = cls()
            record.user_id = user.id
            record.wechat_number = params['wechat_number']
            record.career = params['career']
            record.interested_event = params['interested_event']
            record.best_joined_group = params['best_joined_group']
            record.most_expected_func = params['most_expected_func']
            record.status = UserVerificationRecord.STATUS['approved']
            db.session.add(record)
            db.session.flush()
        return record
