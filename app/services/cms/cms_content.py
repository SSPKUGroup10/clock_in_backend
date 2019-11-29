# -*- coding:utf-8 -*-
from datetime import datetime
from app.utils import StrictSchema, ISO_DATETIME
from marshmallow import fields
from app.models import db, CmsApp, CmsContent, CmsAppModule, CmsPlaybill, CmsEventPackage, CmsType, Event


class PcCmsPlaybillListItemSchema(StrictSchema):
    id = fields.Int(attribute='id')
    status = fields.Int(attribute='status', dump_only=True)

    title = fields.String(attribute='title')
    imageUrl = fields.String(attribute='image_url')
    linkUrl = fields.String(attribute='link_url')
    sequence = fields.Int(attribute='sequence')


class PcCmsEvenPackageListItemSchema(StrictSchema):
    id = fields.Int(attribute='id')
    eventId = fields.Int(attribute='event_id')
    status = fields.Int(attribute='status', dump_only=True)
    title = fields.String(attribute='title')
    coverUrl = fields.String(attribute='cover_url')
    sequence = fields.Int(attribute='sequence')


class PcCmsContentListItemSchema(StrictSchema):
    title = fields.Str(attribute='title', dump_only=True)
    desc = fields.Str(attribute='detail_url', dump_only=True)
    onlineAt = fields.DateTime(attribute='online_at', dump_only=True, format=ISO_DATETIME)
    offlineAt = fields.DateTime(attribute='offline_at', dump_only=True, format=ISO_DATETIME)
    position = fields.Int(attribute='position', dump_only=True)
    cmsType = fields.String(attribute='cms_type', dump_only=True)
    cmsModule = fields.String(attribute='cms_module', dump_only=True)
    status = fields.String(attribute='status', dump_only=True)
    subContent = fields.List(fields.Nested(nested=PcCmsPlaybillListItemSchema), attribute='sub_content')


class Cms:
    def __init__(self):
        self.app_name = None
        self.app_module_name = None
        self.start = None
        self.offset = None
        self.content = None

    def __call__(self, app_name, app_module_name, start, offset):
        self.app_name = app_name
        self.app_module_name = app_module_name
        self.start = start
        self.offset = offset
        self.content = self.return_cms_content()
        return self

    def return_cms_content(self):
        query = db.session.query(CmsApp, CmsAppModule) \
            .filter(CmsApp.app_name == self.app_name,
                    CmsAppModule.module_name == self.app_module_name) \
            .first()
        cms_module = query[1]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ret = db.session.query(CmsContent, CmsType) \
            .join(CmsType, CmsType.id == CmsContent.cms_type_id) \
            .filter(CmsContent.cms_app_module_id == cms_module.id,
                    CmsContent.status == CmsContent.STATUS['online'],
                    CmsContent.position == int(self.start) * int(self.offset),
                    CmsContent.online_at <= now,
                    CmsContent.offline_at >= now).first()
        content_data = None
        if ret:
            cms_content = ret[0]
            cms_type = ret[1]
            cms_content.cms_type = cms_type.name
            cms_content.cms_module = cms_module.module_name
            if cms_type.name == 'playbill':
                playbills = CmsPlaybill.query.filter(CmsPlaybill.cms_content_id == cms_content.id,
                                                     CmsPlaybill.deleted == 0,
                                                     CmsPlaybill.status == CmsPlaybill.STATUS['active']) \
                    .order_by(CmsPlaybill.sequence.asc()).all()

                cms_content.sub_content = playbills
            elif cms_type.name == 'event_package':
                event_package = db.session.query(CmsEventPackage.id, CmsEventPackage.event_id,
                                                 Event.title, Event.cover_url, CmsEventPackage.status,
                                                 CmsEventPackage.sequence) \
                    .filter(CmsEventPackage.cms_content_id == cms_content.id,
                            CmsEventPackage.status == CmsEventPackage.STATUS['active']) \
                    .order_by(CmsEventPackage.sequence.asc()).all()
                cms_content.sub_content = PcCmsEvenPackageListItemSchema(many=True).dump(event_package).data

            else:
                pass
            content_data = {'cms_content': PcCmsContentListItemSchema().dump(cms_content).data}

        return content_data

