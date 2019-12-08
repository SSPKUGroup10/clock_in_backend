from marshmallow import fields, Schema, ValidationError

from app.extensions import db
from app.models.circles import Circle, CircleMemberTable
from app.models.user import User

from app.modules.errors import MISS_DATA, SUCCESS


class CircleSchema(Schema):
    id = fields.Int(dump_only=True, attribute='id')
    name = fields.Str(required=True, attribute='name')
    type = fields.Str(required=True)
    startAt = fields.DateTime(attribute='start_at')
    endAt = fields.DateTime(attribute='end_at')
    desc = fields.Str()
    checkRule = fields.Str(attribute='check_rule', required=True)
    circleMasterId = fields.Int(attribute='circle_master_id', required=True)
    avatar = fields.Str()

    class Meta:
        datetimeformat = '%Y-%m-%d %H:%M:%S'


class CircleList:

    def get(self):
        cirlcles = Circle.query.all()
        schema = CircleSchema(many=True)
        print("*" * 100)
        print(cirlcles)
        print(type(cirlcles))
        result = schema.dump(cirlcles)
        return result

    def create(self, **kwargs):
        from . import jwt
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
        CircleMemberTable.add(model, jwt.visitor)
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


class JoinCircleSchema(Schema):
    circleID = fields.Int(required=True, attribute='circle_id')
    UserID = fields.Int(required=True, attribute="user_id")


class CircleMembeSchema(Schema):
    UserID = fields.Int(attribute="user_id")
    avatar = fields.Str()
    Username = fields.Int(attribute="username")


class CircleMember:
    def __init__(self, circle_id):
        self.circle = Circle.query.filter_by(id=circle_id).first()


    def join_circle(self, **kwargs): # 加入圈子
        schema = JoinCircleSchema()
        # 如果有字段缺失错误，就会自动抛出来，被自动处理
        result = schema.load(kwargs)
        circle_id = result.get('circle_id', -1)
        user_id = result.get('user_id', -1)
        # TODO 校验是否是本人

        circle = self.circle
        user = User.query.filter_by(id=user_id).first()
        flag = True
        if not circle:
            MISS_DATA['field'] = 'circle_id'
            flag = flag and False
        if not user:
            MISS_DATA['field'] = 'user_id'
            flag = flag and False
        if not flag:
            raise ValidationError(message=MISS_DATA)
        CircleMemberTable.add(circle, user)
        return SUCCESS

    def members_of_circle(self): # 圈子成员列表
        pass

    def clock_in(self): # 打卡
        pass