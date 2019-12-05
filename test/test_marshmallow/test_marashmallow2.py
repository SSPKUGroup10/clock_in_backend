# coding=utf-8
# 测试把一个对象转换成字符串

from datetime import datetime
from marshmallow import fields, Schema


class TestObjSchema(Schema):
    aA = fields.Int(attribute='a_a')
    bB = fields.Int(attribute='b_a')
    cC = fields.DateTime(attribute='c_c')

    class Meta:
        datetimeformat = '%Y-%m-%d %H:%M:%S'


class TestObj:
    a_a = 1
    b_b = 2
    c_c = datetime.now()

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
    a = {"bB": 2, "aA": 1, "cC": "2019-11-29 19:44"}
    # print(TestObjSchema().load(a)) # UnmarshalResult(data={}, errors={'_schema': ['Invalid input type.']})

