from marshmallow import fields, Schema

from app.extensions import db
from app.models.test_model import TestModel


class TestObjSchema(Schema):
    a = fields.Int()
    b = fields.Int()


class TestModelSchema(Schema):
    attr1 = fields.Str()
    attr2 = fields.Int()
    attr3 = fields.DateTime()
    id = fields.Str()
    uuid = fields.Str()

    class Meta:
        dateformat = "%Y-%m-%d %H:%M:%S"


class TestObj:
    a = 1
    b = 2

    def __init__(self):
        pass

    def __str__(self):
        return "a={}, b={}".format(self.a, self.b)

    def get(self):
        return TestObjSchema().dump(self).data


class TestModelEntity:
    def create(self, **kwargs):
        schema = TestModelSchema()
        data = schema.load(kwargs).data
        model = TestModel()
        model.attr1 = data['attr1']
        model.attr2 = data['attr2']
        model.attr3 = data['attr3']
        db.save(model)
        return schema.dump(model).data

