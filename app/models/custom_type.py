# -*- utf-8 -*-

from app.extensions import db


class CustomType(db.Model):
    __tablename__='custom_type'
    
    name = db.Column(db.String(8))
    sequence = db.Column(db.Integer, default=100)
    
    @classmethod
    def init_db(cls, custom_types):
        try:
            for custom_type in custom_types:
                name = custom_type[0]
                sequence = custom_type[1]
                custom = cls.query.filter_by(name=name).first()
                if custom is None:
                    custom = cls()
                    custom.name = name
                custom.sequence = sequence
                db.session.add(custom)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
