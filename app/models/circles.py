from app.extensions import db


class Circle(db.Model):
    __tablename__ = 'circles'
    name = db.Column(db.String(32))
    type = db.Column(db.String(8))
    start_at = db.Column(db.DateTime())
    end_at = db.Column(db.DateTime())
    desc = db.Column(db.String(128))
    check_rule = db.Column(db.String(256))
    circle_master_id = db.Column(db.Integer())
    avatar = db.Column(db.String(256)) # 头像地址
    joined_number = db.Column(db.Integer()) # 加入人数
    is_published = db.Column(db.Integer()) # 草稿状态为0，没有发布，发布状态为1， 已经发布

    def update_joined_number(self):
        self.joined_number += 1


class CircleMemberTable(db.Model):
    __tablename__ = 'circles_members'
    circle_id = db.Column(db.Integer(), index=True)  # 圈子id
    user_id = db.Column(db.Integer(), index=True)  # 用户ID

    @classmethod
    def add(cls, circle, user):
        obj = cls()
        obj.user_id = user.id
        obj.circle_id = circle.id
        db.save(obj)
        return obj
