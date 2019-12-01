# -*- coding:utf-8 -*-
from calendar import monthrange
from datetime import datetime, date, timedelta
from sqlalchemy import asc, desc
from flask import request
from app.extensions import celery
from sqlalchemy.orm import aliased
from app.modules.services import wechat_obj
from app.utils import BusinessError, ListInterface, ItemInterface, api, ISO_DATETIME
from app.models import db, Event, EventTicketType, SupportedCity, User, EventOrder, EventTicketAudit, \
    EventTicket, ShareAwardRecord, Admin, EventCustomType, CustomType, EventUserCustomInfo
from app.modules.schemas import EventSchema, MobileEventListSchema, MobileEventCommitSchema, \
    MobileEventTicketAuditListSchema, MobileEventTicketAuditSchema, MobileEventTicketListSchema, MobileEventCustomListSchema
from app.modules.errors import YOOQUN_ERRORS
from app.modules.mobile.logger import logger
from .base import EntityMobileEventBase
from app.modules.utils import EventTask
from app.services import Cms


class EventQueryBuilder:
    @classmethod
    def _build_date_query(cls, query, kwargs):
        d = kwargs.get('filter_date')
        if d:
            today = date.today()
            if d == 'all':
                pass
            elif d == 'week':
                weekday = today.weekday()
                monday = today - timedelta(days=weekday)
                next_monday = today + timedelta(days=6 - weekday) + timedelta(days=1)
                query = query.filter(Event.start_at >= monday).filter(Event.start_at < next_monday)
            elif d == 'weekend':
                weekday = today.weekday()
                if weekday < 5:
                    saturday = today + timedelta(days=5 - weekday)
                    next_monday = saturday + timedelta(days=2)
                elif weekday == 5:
                    saturday = today
                    next_monday = today + timedelta(days=2)
                else:
                    saturday = today - timedelta(days=1)
                    next_monday = today + timedelta(days=1)
                query = query.filter(Event.start_at >= saturday).filter(Event.start_at < next_monday)
                pass
            elif d == 'month':
                month, days = monthrange(today.year, today.month)
                first_day = today.replace(day=1)
                next_first_day = today.replace(day=days) + timedelta(days=1)
                query = query.filter(Event.start_at >= first_day).filter(Event.start_at < next_first_day)
        return query

    @classmethod
    def _build_price_query(cls, query, kwargs):
        p = kwargs.get('filter_price')
        if p:
            if p == 'all':
                pass
            elif p == 'charge':
                query = query.filter(Event.high_price != 0)
            elif p == 'free':
                query = query.filter(Event.high_price == 0)
        return query

    @classmethod
    def _build_search_query(cls, query, kwargs):
        q = kwargs.get('q')
        if q:
            query = query.filter(Event.title.like('%' + q + '%'))
        return query

    @classmethod
    def build_query(cls, query, kwargs):
        query = cls._build_date_query(query, kwargs)
        query = cls._build_price_query(query, kwargs)
        query = cls._build_search_query(query, kwargs)
        return query


class EntityEventList(ListInterface, EventQueryBuilder):
    def __init__(self, user):
        self.user = user

    @api('mobile', 'events', logger)
    def get(self, **kwargs):
        query = Event.query.filter_by(status=Event.STATUS['audited'], is_public=True)
        query = self.build_query(query, kwargs)

        query = query.order_by(desc(Event.on_top),
                               asc(Event.timing_status),
                               asc(Event.sequence),
                               asc(Event.start_at))

        ret = query.get_list_for_mobile(page=kwargs.get('page'))
        ret = MobileEventListSchema().dump(ret).data
        cms = Cms()
        cms_event = cms('mobile', 'event', kwargs.get('page') or 1, kwargs.get('perPage') or 10).content
        cms_index = cms('mobile', 'event', 0, 0).content

        return ret, cms_index, cms_event

    @api('mobile', 'events', logger)
    def create(self, **kwargs):
        try:
            auditing_count = Event.query.filter_by(status=Event.STATUS['committed'], user_id=self.user.id).count()
            if auditing_count > 5:
                return {'event': None, 'reason': '您已经提交了5个活动，请耐心等待审核！'}

            event = Event.query.filter_by(status=Event.STATUS['draft'], user_id=self.user.id).first()
            # 设置组织这信息默认选项
            pre_event = Event.query.filter_by(status=Event.STATUS['audited'], user_id=self.user.id)\
                    .order_by(desc(Event.updated_at)).first()
            if event is None:
                event = Event()
                event.user_id = self.user.id
                event.group_id = self.user.group_id
                event = db.save(event)
            event.ticket_types = EventTicketType.query.filter_by(event_id=event.id) \
                .order_by(asc(EventTicketType.sequence)).all()
            
            event.custom_options = CustomType.query.order_by(asc(CustomType.sequence)).all()
            event.custom_types = EventCustomType.query.filter_by(event_id=event.id)\
                .order_by(asc(EventCustomType.sequence)).all()
            
            if pre_event:
                event.organizer = pre_event.organizer
            return {'event': EventSchema().dump(event).data}
        except Exception as e:
            print(e)
            db.session.rollback()
            raise e


class EntityEventItem(EntityMobileEventBase, ItemInterface, EventTask):
    def __init__(self, event_uuid, user):
        super().__init__(event_uuid, user)

    def _rebuild_params(self, params):
        if params.get('city_uuid'):
            city = SupportedCity.query.get_by_uuid(params['city_uuid'])
            if city:
                params['province_id'] = city.province_id
                params['province'] = city.province_name
                params['city_id'] = city.city_id
                params['city'] = city.city_name
                params.pop('city_uuid')
        if params.get('time_range'):
            times = params['time_range'].split(',')
            params['start_at'] = times[0]
            params['end_at'] = times[1]
            params['apply_end_at'] = params['start_at']
            if len(times) == 3:
                params['apply_end_at'] = times[2]
            params.pop('time_range')

        return params

    def delete(self):
        pass

    def _add_event_view(self):
        celery.send_task('tasks.event.add_event_view',
                         [self.event.id, self.user.id,
                          request.headers.get('X-Real-Ip') or request.remote_addr,
                          request.headers.get('User-Agent'),
                          datetime.now().strftime(ISO_DATETIME)])

    @api('mobile', 'event', logger)
    def view(self, **kwargs):
        ret = self.get()
        if ret:
            ShareAwardRecord.create_record(kwargs.get('shareCode'),
                                           ShareAwardRecord.RECORD_TYPES['view'],
                                           self.user.id)
        return ret

    @property
    def ticket_types(self):
        return EventTicketType \
            .query.filter_by(event_id=self.event.id, status=EventTicketType.STATUS['activated']) \
            .order_by(asc(EventTicketType.sequence)).all()

    @property
    def custom_types(self):
        return EventCustomType.query.filter_by(event_id=self.event.id)\
                .order_by(asc(EventCustomType.sequence)).all()
    
    @property
    def custom_options(self):
        return CustomType.query.order_by(asc(CustomType.sequence)).all()

    @property
    def unpaid_order(self):
        order = EventOrder.query.filter_by(event_id=self.event.id,
                                           user_id=self.user.id,
                                           status=EventOrder.STATUS['unpaid']).first()
        if order:
            now = int(datetime.now().timestamp())
            expired = int(order.expired_time.timestamp())
            count_down = 0
            if expired > now:
                count_down = expired - now
            order = {
                'orderUuid': order.uuid,
                'desc': order.desc,
                'countDown': count_down,
                'amount': order.amount,
                'expiredTime': order.expired_time.strftime(ISO_DATETIME)
            }
        return order

    @property
    def my_ticket_types(self):
        types = db.session.query(EventTicket.event_ticket_type_id) \
            .filter_by(event_id=self.event.id, buyer_id=self.user.id) \
            .group_by(EventTicket.event_ticket_type_id) \
            .all()
        return types

    def get(self):
        self._add_event_view()
        self.event.ticket_types = self.ticket_types
        self.event.publisher = User.query.get(self.event.user_id)
        self.event.unpaid_order = self.unpaid_order
        self.event.my_ticket_types = self.my_ticket_types
        self.event.custom_options = self.custom_options
        self.event.custom_types = self.custom_types
        ret = EventSchema().dump(self.event).data
        return ret

    def _touch_modify(self):
        if not self.event_owner:
            raise BusinessError('API Error', YOOQUN_ERRORS['DataRelationError'][1],
                                YOOQUN_ERRORS['DataRelationError'][0])
        if self.event.status not in [Event.STATUS['draft'], Event.STATUS['rejected']]:
            raise BusinessError('API Error', '活动不是草稿状态', YOOQUN_ERRORS['APITimingError'][0])

    @api('mobile', 'event', logger)
    def update(self, **kwargs):
        if not self.event_owner:
            raise BusinessError('API Error', YOOQUN_ERRORS['DataRelationError'][1],
                                YOOQUN_ERRORS['DataRelationError'][0])
        if self.event.status_code in ['ongoing', 'ended']:
            raise BusinessError('API Error', '活动在进行中或者已结束，不能修改！', YOOQUN_ERRORS['APITimingError'][0])

        params = EventSchema().load(kwargs).data
        self._rebuild_params(params)
        need_renotify = False
        if self.event.status == Event.STATUS['audited']:
            start_at = params.get('start_at')
            if start_at:
                start_at = datetime.strptime(start_at, ISO_DATETIME)
                if start_at != self.event.start_at:
                    need_renotify = True
            location = params.get('location')
            if location:
                if location != self.event.location:
                    need_renotify = True
            end_at = params.get('end_at')
            if end_at:
                end_at = datetime.strptime(end_at, ISO_DATETIME)
                if end_at != self.event.end_at:
                    need_renotify = True

        self.event = db.update(self.event, params)

        if need_renotify:
            self.setup_tasks(self.event, need_renotify)

        return {'eventUuid': self.event.uuid}

    @api('mobile', 'event', logger)
    def commit(self, **kwargs):
        self._touch_modify()
        self.check_fields(MobileEventCommitSchema, self.event)
        if len(self.ticket_types) == 0:
            raise BusinessError('APITimingError', '您还没有创建票种！', YOOQUN_ERRORS['APITimingError'][0])
        
        audit = self.event.commit_event()
        wechat_obj.wechat_notifier.work_order_remind(Admin.query.get(1).openid,
                                                     '新建活动, 审核单号-{0}'.format(audit.audit_number), self.user,
                                                     '活动 【{0}】提交审核通知'.format(self.event.title))
        return {'eventUuid': self.event.uuid}

    @api('mobile', 'event', logger)
    def cancel(self, **kwargs):
        self._touch_modify()
        self.event.status = Event.STATUS['canceled']
        db.save(self.event)
        return {'eventUuid': self.event.uuid}

    @api('mobile', 'event', logger)
    def get_audit_list(self, **kwargs):
        if self.event_owner is False:
            raise BusinessError('User Auth Error', YOOQUN_ERRORS['UserAuthError'][1], YOOQUN_ERRORS[0])
        user = aliased(User, name='user')
        avatar_url = user.avatar_url.label('avatar_url')
        query = db.session.query(EventTicketAudit.uuid,
                                 EventTicketAudit.status,
                                 EventTicketAudit.user_id,
                                 EventTicketAudit.buyer_name,
                                 EventTicketAudit.buyer_phone, avatar_url)
        query = query.join(user, user.id == EventTicketAudit.user_id)
        query = query.filter(EventTicketAudit.event_id == self.event.id)
        query = query.order_by(EventTicketAudit.id.desc())
        ret = query.get_list_for_mobile(kwargs.get('page'), kwargs.get('perPage') or 50)
        return MobileEventTicketAuditListSchema().dump(ret).data

    @api('mobile', 'event', logger)
    def get_tickets_list(self, **kwargs):
        if self.event_owner is False:
            raise BusinessError('User Auth Error', YOOQUN_ERRORS['UserAuthError'][1], YOOQUN_ERRORS[0])
        user = aliased(User, name='user')
        avatar_url = user.avatar_url.label('avatar_url')
        user_uuid = user.uuid.label('user_uuid')
        
        query = db.session.query(EventTicket.uuid,
                                 EventTicket.status,
                                 EventTicket.holder_name,
                                 EventTicket.holder_phone, avatar_url, user_uuid, 
                                 EventTicket.ticket_type_name)
        
        query = query.join(user, user.id == EventTicket.holder_id)
        query = query.filter(EventTicket.event_id == self.event.id,
                             EventTicket.status >= 0)
        query = query.order_by(EventTicket.id.desc())
        
        ret = query.get_list_for_mobile(kwargs.get('page'), kwargs.get('perPage') or 50)
        return MobileEventTicketListSchema().dump(ret).data


class EntityTicketAuditItem(EntityMobileEventBase, ItemInterface):
    def __init__(self, event_uuid, audit_uuid, user):
        super().__init__(event_uuid, user)
        audit = EventTicketAudit.query.filter_by(uuid=audit_uuid).first()
        self.audit = audit

    def delete(self):
        pass
    
    @api('mobile', 'ticket_audits', logger)
    def get(self):
        if self.event_owner is False:
            raise BusinessError('User Auth Error', YOOQUN_ERRORS['UserAuthError'][1], YOOQUN_ERRORS[0])
        
        tmp_dict = {}
        
        user = User.query.filter_by(id=self.audit.user_id).first()
        # 获取自定义信息
        order = EventOrder.query.filter_by(event_id=self.event.id,
                                           event_ticket_type_id=self.audit.ticket_type_id,
                                           user_id=self.audit.user_id,
                                           price=0).first()
        custom_info = EventUserCustomInfo.query.filter_by(user_id=self.audit.user_id, 
                                                          order_id=order.id, 
                                                          ticket_type_id=self.audit.ticket_type_id)\
                   .order_by(asc(EventUserCustomInfo.sequence)).all()

        tmp_dict['uuid'] = self.audit.uuid
        tmp_dict['holder_name'] = self.audit.buyer_name
        tmp_dict['holder_phone'] = self.audit.buyer_phone
        tmp_dict['avatar_url'] = user.avatar_url
        tmp_dict['custom_infos'] = custom_info
        return MobileEventCustomListSchema().dump(tmp_dict).data

    @api('mobile', 'event_ticket_audit', logger)
    def update(self, **kwargs):
        if self.event_owner is False:
            raise BusinessError('User Auth Error', YOOQUN_ERRORS['UserAuthError'][1], YOOQUN_ERRORS[0])

        if self.audit is None:
            raise BusinessError('Data not Found', YOOQUN_ERRORS['DataNotFound'][1], YOOQUN_ERRORS['DataNotFound'][0])
        if self.audit.status != EventTicketAudit.STATUS['committed']:
            raise BusinessError('Data not Allowed', '已经审核过该报名申请', YOOQUN_ERRORS['DataNotAllowed'][0])
        params = MobileEventTicketAuditSchema().load(kwargs).data
        if params['operation'] == 'approve':
            self.audit.status = EventTicketAudit.STATUS['audited']
            ticket_type = EventTicketType.query.get(self.audit.ticket_type_id)
            buyer = User.query.get(self.audit.user_id)
            order = EventOrder.query.filter_by(event_id=self.event.id,
                                               event_ticket_type_id=ticket_type.id,
                                               user_id=self.audit.user_id,
                                               price=0).first()
            # 创建票
            ticket = EventTicket.create_ticket(self.event, order, ticket_type, buyer)
            db.session.add(ticket)
            db.session.flush()
            # 更新票的数量
            ticket_type.update_quantities()
            db.session.add(ticket_type)
            db.session.flush()
            self.event.update_quantities()
            db.session.add(self.event)

        if params['operation'] == 'reject':
            self.audit.status = EventTicketAudit.STATUS['reject']
        db.session.add(self.audit)
        db.session.commit()
        return {'auditUuid': self.audit.uuid, 'msg': params['operation'] + "  " + 'success'}


class EntityTicketItem(EntityMobileEventBase, ItemInterface):
    def __init__(self, event_uuid, ticket_uuid, user):
        super().__init__(event_uuid, user)
        ticket = EventTicket.query.filter_by(uuid=ticket_uuid).first()
        self.ticket = ticket
    
    @api('mobile', 'tickets', logger)
    def get(self):
        if self.event_owner is False:
            raise BusinessError('User Auth Error', YOOQUN_ERRORS['UserAuthError'][1], YOOQUN_ERRORS[0])
        
        tmp_dict = {}
        user = User.query.filter_by(id=self.ticket.holder_id).first()
        custom_info = EventUserCustomInfo.query.filter_by(user_id=user.id, 
                                                          order_id=self.ticket.event_order_id, 
                                                          ticket_type_id=self.ticket.event_ticket_type_id)\
                                                          .order_by(asc(EventUserCustomInfo.sequence)).all()
        
        tmp_dict['uuid'] = self.ticket.uuid
        tmp_dict['holder_name'] = self.ticket.holder_name
        tmp_dict['holder_phone'] = self.ticket.holder_phone
        tmp_dict['avatar_url'] = user.avatar_url
        tmp_dict['custom_infos'] = custom_info
        
        return MobileEventCustomListSchema().dump(tmp_dict).data
    
