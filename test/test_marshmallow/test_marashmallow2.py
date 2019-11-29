# coding=utf-8
# 测试把一个对象转换成字符串

from datetime import datetime
from marshmallow import fields, Schema




class TestObjSchema(Schema):
    a = fields.Int(attribute='a')
    b = fields.Int(attribute='b')
    c = fields.DateTime()

    class Meta:
        dateformat = '%Y-%m-%d %H:%M:%S'


class TestObj:
    a = 1
    b = 2
    c = datetime.now()

    def __init__(self):
        pass

    def __str__(self):
        return "a={}, b={}".format(self.a, self.b)

    def get(self):
        return TestObjSchema().dump(self).data


# 测试把一个对象输出成字符串
if __name__ == '__main__':
    print(type(datetime.now()))
    # MarshalResult(data={'a': 1, 'b': 2}, errors={})
    print(TestObjSchema().dump(TestObj()))
    a = {"b": 2, "a": 1, "c": "2019-11-29 19:44:17"}
    print(TestObjSchema().load(a).data) # UnmarshalResult(data={}, errors={'_schema': ['Invalid input type.']})

