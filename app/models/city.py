# -*- coding:utf-8 -*-
import csv
from app.extensions import db


class ZoneFinder:

    @classmethod
    def get_zones(cls, filename):
        zones = []
        with open(filename, 'rt', encoding='utf-8') as csv_file:
            rows = csv.reader(csv_file)
            for row in rows:
                code = row[0]
                name = row[1]
                if name in ['北京市', '天津市', '上海市', '重庆市']:
                    zones.append(['municipality', code, name])
                elif str(code).endswith('0000', 2):
                    zones.append(['province', code, name])
                elif str(code).endswith('00', 4):
                    zones.append(['city', code, name])
                else:
                    zones.append(['district', code, name])
        return zones


class BaseProvince(db.Model):
    __tablename__ = 'base_province'
    code = db.Column(db.String(6))
    name = db.Column(db.String(24))

    cities = db.relationship('BaseCity', backref='province', lazy=True)

    @classmethod
    def init_db(cls, zones):
        try:
            for zone in zones:
                zone_type = zone[0]
                code = zone[1]
                name = zone[2]
                if zone_type in ['province', 'municipality']:
                    province = cls.query.filter_by(code=code).first()
                    if province is None:
                        province = cls()
                        province.code = code
                        province.name = name
                        db.session.add(province)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @classmethod
    def get_province_by_sub_code(cls, code):
        try:
            code = code[:2] + '0000'
            return cls.query.filter_by(code=code).first()
        except Exception as e:
            print(e)
            return None


class BaseCity(db.Model):
    __tablename__ = 'base_city'
    code = db.Column(db.String(6))
    name = db.Column(db.String(24))

    province_id = db.Column(db.Integer, db.ForeignKey("base_province.id"))

    @classmethod
    def init_db(cls, zones):
        try:
            for zone in zones:
                zone_type = zone[0]
                code = zone[1]
                name = zone[2]
                if zone_type in ['city', 'municipality']:
                    province = BaseProvince.get_province_by_sub_code(code)
                    city = cls.query.filter_by(code=code).first()
                    if province and city is None:
                        city = cls()
                        city.province_id = province.id
                        city.code = code
                        city.name = name
                        db.session.add(city)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class SupportedCity(db.Model):
    __tablename__ = 'supported_city'
    city_id = db.Column(db.Integer, nullable=False, index=True)
    city_code = db.Column(db.String(6))
    city_name = db.Column(db.String(24))

    province_id = db.Column(db.Integer, nullable=False, index=True)
    province_code = db.Column(db.String(6))
    province_name = db.Column(db.String(24))

    activated = db.Column(db.Boolean, default=True)
