from marshmallow import fields, Schema, ValidationError

from app.extensions import db
from app.models.circles import Circle


class CircleSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    type = fields.Str(required=True)
    start_at = fields.DateTime()
    end_at = fields.DateTime()
    desc = fields.Str()
    check_rule = fields.Str(required=True)
    circle_master_id = fields.Int(required=True)
    avatar = fields.Str()

    class Meta:
        dateformat = "%Y-%m-%d %H:%M:%S"


class CircleList:
    a = 1
    b = 2

    def __init__(self):
        pass

    def __str__(self):
        return "a={}, b={}".format(self.a, self.b)

    def get(self):
        cirlcles = Circle.query.all()
        schema = CircleSchema(many=True)
        print("*" * 100)
        print(cirlcles)
        print(type(cirlcles))
        result = schema.dump(cirlcles)
        return result

    def create(self, **kwargs):
        schema = CircleSchema()
        try:
            result = schema.load(kwargs)
        except ValidationError as err:
            return err.messages
        data = result
        model = Circle()
        model.name = data['name']
        model.type = data['type']
        model.start_at = data.get('start_at', '1900-01-01 00:00:00')
        model.end_at = data.get('end_at', '1900-01-01 00:00:00')
        model.desc = data.get('desc')
        model.check_rule = data.get('check_rule')
        model.circle_master_id = data.get('circle_master_id', 0)
        model.avatar = data.get('avatar', '')
        db.save(model)
        return schema.dump(model)

class CircleItem:
    pass

