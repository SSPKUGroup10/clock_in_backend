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

    def get(self, id):
        circle = Circle.query.filter_by(id=id).first()
        if circle:
            schema = CircleSchema()
            result = schema.dump(circle)
            return result
        else:
            return {}

    def update(self, id, update_data):
        circle = Circle.query.filter_by(id=id).first()
        if circle:
            valid_update_dict = {}
            valid_update_dict['name'] = update_data.get('name', '')
            if valid_update_dict.get('name'):
                circle.name = valid_update_dict.get('name')
                db.save(circle)
            schema = CircleSchema()
            result = schema.dump(circle)
            return result
        else:
            return {}

    def delete(self, id):
        circle = Circle.query.filter_by(id=id).first()
        if circle:
            db.session.delete(circle)
            return {"msg": "删除成功"}
        else:
            return {"msg": "对象不存在"}

