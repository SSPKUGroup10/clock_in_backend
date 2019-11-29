# -*- coding:utf-8 -*-
from app.extensions import db


class CmsApp(db.Model):
    __tablename__ = 'cms_app'

    app_name = db.Column(db.String(24))
    app_name_desc = db.Column(db.String(128))
    default = db.Column(db.Boolean, default=False)

    @classmethod
    def init_db(cls, cms_app):
        try:
            for ad in cms_app:
                app_name = ad[0]
                app_name_desc = ad[1]
                default = ad[2]
                app = CmsApp.query.filter_by(app_name=app_name).first()
                if app is None:
                    app = CmsApp()
                    app.app_name = app_name
                    app.app_name_desc = app_name_desc
                    app.default = default
                    db.session.add(app)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class CmsAppModule(db.Model):
    __tablename__ = 'cms_app_module'

    cms_app_id = db.Column(db.Integer, index=True)
    module_name = db.Column(db.String(24))
    module_desc = db.Column(db.String(128))
    default = db.Column(db.Boolean, default=False)

    @classmethod
    def init_db(cls, modules):
        try:
            for ad in modules:
                app_name = ad[0]
                module_name = ad[1]
                module_desc = ad[2]
                default = ad[3]
                app_module = CmsAppModule.query.filter_by(module_name=module_name).first()
                app_name_id = CmsApp.query.filter_by(app_name=app_name).first()
                if app_name_id:
                    app_id = app_name_id.id
                else:
                    app_id = 0
                if app_module is None:
                    app_module = CmsAppModule()
                    app_module.cms_app_id = app_id
                    app_module.module_name = module_name
                    app_module.module_desc = module_desc
                    app_module.default = default
                    db.session.add(app_module)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class CmsType(db.Model):
    __tablename__ = 'cms_type'

    name = db.Column(db.String(24))
    desc = db.Column(db.String(128))
    instruction = db.Column(db.String(128))
    instruction_image_url = db.Column(db.String(1024))
    default = db.Column(db.Boolean, default=False)

    @classmethod
    def init_db(cls, types):
        try:
            for ad in types:
                name = ad[0]
                desc = ad[1]
                default = ad[2]
                cms_type = CmsType.query.filter_by(name=name).first()
                if cms_type is None:
                    cms_type = CmsType()
                    cms_type.name = name
                    cms_type.desc = desc
                    cms_type.default = default
                    db.session.add(cms_type)

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e


class CmsContent(db.Model):
    __tablename__ = 'cms_content'

    STATUS = {
        'draft': 0,
        'online': 1,
        'offline': -1
    }

    title = db.Column(db.String(24))
    cover_url = db.Column(db.String(1024))
    link_url = db.Column(db.String(1024))
    detail_url = db.Column(db.String(1024))
    position = db.Column(db.Integer)
    online_at = db.Column(db.DateTime)
    offline_at = db.Column(db.DateTime)

    cms_app_module_id = db.Column(db.Integer)
    cms_type_id = db.Column(db.Integer)

    status = db.Column(db.Integer, default=STATUS['draft'])


class CmsPlaybill(db.Model):
    __tablename__ = 'cms_playbill'

    STATUS = {
        'active': 1,  # 激活
        'deactivate': -1  # 去激活
    }

    cms_content_id = db.Column(db.Integer, index=True)
    # 海报名称
    title = db.Column(db.String(128))
    # 海报地址
    image_url = db.Column(db.String(1024))
    link_url = db.Column(db.String(1024))
    sequence = db.Column(db.Integer, default=100)
    status = db.Column(db.Integer, default=STATUS['deactivate'])

    @classmethod
    def rebuild_sequence(cls, se_list):
        playbills = CmsPlaybill.query.filter(CmsPlaybill.id.in_(se_list)).all()
        for playbill in playbills:
            for id in se_list:
                if playbill.id == id:
                    playbill.sequence = se_list.index(id)
                    db.session.add(playbill)

        db.session.commit()

        return CmsPlaybill.query.filter(CmsPlaybill.id.in_(se_list)).order_by(CmsPlaybill.sequence).all()


class CmsEventPackage(db.Model):
    __tablename__ = 'cms_event_package'

    STATUS = {
        'active': 1,  # 激活
        'deactivate': -1  # 去激活
    }

    cms_content_id = db.Column(db.Integer, index=True)
    event_id = db.Column(db.Integer, index=True)
    sequence = db.Column(db.Integer, default=100)
    status = db.Column(db.Integer, default=STATUS['deactivate'])

    @classmethod
    def rebuild_sequence(cls, se_list):
        events = CmsEventPackage.query.filter(CmsEventPackage.id.in_(se_list)).all()
        for package in events:
            for id in se_list:
                if package.id == id:
                    package.sequence = se_list.index(id)
                    db.session.add(package)

        db.session.commit()

        return CmsEventPackage.query.filter(CmsEventPackage.id.in_(se_list)).order_by(CmsEventPackage.sequence).all()

