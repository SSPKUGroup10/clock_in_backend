
from marshmallow import fields, Schema


class TestObjSchema(Schema):
    a = fields.Int()
    b = fields.Int()


class TestObj:
    a = 1
    b = 2

    def __init__(self):
        pass

    def __str__(self):
        return "a={}, b={}".format(self.a, self.b)

    def get(self):
        return TestObjSchema().dump(self).data


