# coding=utf-8
# 测试把一个对象转换成字符串

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

# 测试把一个对象输出成字符串
if __name__ == '__main__':
    print(TestObj().get())
    a = "{'b': 2, 'a': 1}"
    print(TestObjSchema().load(a))

