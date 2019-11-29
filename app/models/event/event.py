# -*- coding:utf-8 -*-
from sqlalchemy import and_, func, or_
from werkzeug.exceptions import NotFound
from datetime import datetime, timedelta
from app.extensions import db
from app.utils import TIMESTAMP, generate_code_string
from app.models.user import User, UserWechat
from app.models.audit import Audit
from app.models.custom_type import CustomType
from app.models.marketing.share_award import ShareAwardRecord
from app.models.transaction import Transaction
from .._base import BaseUserAgent


class Event(db.Model):
    __tablename__ = 'event'

    STATUS = {
        'draft': 0,  # 草稿
        'committed': 1,  # 待审核
        'audited': 2,  # 已审核通过
        'canceled': -1,  # 已取消
        'rejected': -2,  # 已驳回
        'forbid': -3,  # 已禁止
        'offline': -4  # 已下线
    }

    TIMING_STATUS = {
        'applying': 0,
        'preparing': 1,
        'ongoing': 2,
        'finished': 3,
        'closed': 4
    }

    title = db.Column(db.String(128))
    cover_url = db.Column(db.String(2048))
    summary = db.Column(db.String(1024))

    group_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    organizer = db.Column(db.String(1024))

    start_at = db.Column(db.DateTime)
    end_at = db.Column(db.DateTime)
    apply_end_at = db.Column(db.DateTime)

    ticket_left_quantity = db.Column(db.Integer, default=0)
    ticket_quantity = db.Column(db.Integer, default=0)

    province_id = db.Column(db.Integer)
    province = db.Column(db.String(24))
    city_id = db.Column(db.Integer)
    city = db.Column(db.String(32))
    location = db.Column(db.String(128))

    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)

    tags = db.Column(db.String(36))

    detail_url = db.Column(db.String(2048))
    status = db.Column(db.Integer, default=STATUS['draft'])
    timing_status = db.Column(db.Integer, default=TIMING_STATUS['applying'])

    is_public = db.Column(db.Boolean, default=True)

    low_price = db.Column(db.Integer)
    high_price = db.Column(db.Integer)

    on_top = db.Column(db.Boolean, default=False)
    on_group_top = db.Column(db.Boolean, default=False)
    sequence = db.Column(db.Integer, default=100)

    share_award_rate = db.Column(db.Integer, default=0)

    view_total = db.Column(db.Integer, default=0)
    reject_reason = db.Column(db.String(128))

    m_openid = db.Column(db.String(32))
    m_body_html = db.Column(db.TEXT)
    m_activity_id = db.Column(db.Integer)

    @property
    def status_code(self):
        if self.status == self.STATUS['draft']:
            return 'draft'
        elif self.status == self.STATUS['committed']:
            return 'committed'
        elif self.status == self.STATUS['audited']:
            now = datetime.now()
            if self.apply_end_at is None or self.start_at is None or self.end_at is None:
                return 'timeNone'
            if now < self.apply_end_at:
                return 'applying'
            if self.apply_end_at <= now < self.start_at:
                return 'preparing'
            if self.start_at <= now < self.end_at:
                return 'ongoing'
            if now >= self.end_at:
                return 'ended'
            return 'timeError'
        elif self.status == -1:
            return 'cancelled'
        elif self.status == -2:
            return 'rejected'
        elif self.status == -3:
            return 'forbid'
        elif self.status == -4:
            return 'offline'
        else:
            return 'unknown'


    @property
    def has_group(self):
        return True if self.group_id else False

    @property
    def join_number(self):
        "参加这个活动的人数, 目前取买票的人"
        return EventTicket.query.filter(EventTicket.event_id==self.id).count()

    @property
    def user_openid(self):
        return UserWechat.query.filter_by(user_id=self.user_id).first().public_openid

    def update_quantities(self):
        result = db.session.query(func.sum(EventTicketType.ticket_left_quantity).label('left_quantity'),
                                  func.sum(EventTicketType.ticket_quantity).label('total_quantity')) \
            .filter(and_(EventTicketType.event_id == self.id,
                         EventTicketType.status != EventTicketType.STATUS['draft'])) \
            .first()
        self.ticket_left_quantity = int(result.left_quantity or 0)
        self.ticket_quantity = int(result.total_quantity or 0)

    def update_prices(self):
        result = db.session.query(func.min(EventTicketType.price).label('lowest_price'),
                                  func.max(EventTicketType.price).label('highest_price')) \
            .filter(and_(EventTicketType.event_id == self.id,
                         EventTicketType.status != EventTicketType.STATUS['draft'])) \
            .first()
        self.low_price = int(result.lowest_price or 0)
        self.high_price = int(result.highest_price or 0)

    def commit_event(self):
        if self.status != Event.STATUS['committed']:
            audit = Audit.create(Audit.AUDIT_TYPES['event'], self.uuid, '活动: {0.title}'.format(self))
            self.status = Event.STATUS['committed']
            db.session.add(self)
            db.session.commit()
            return audit
        return None


class EventType(db.Model):
    name = db.Column(db.String(24))
    description = db.Column(db.String(1024))


class EventTag(db.Model):
    __tablename__ = 'event_tag'
    event_id = db.Column(db.Integer)
    tag_id = db.Column(db.Integer)
    sequence = db.Column(db.Integer, default=1000)


class EventChangeHistory(db.Model, BaseUserAgent):
    __tablename__ = 'event_change_history'
    event_id = db.Column(db.Integer, index=True)
    desc = db.Column(db.String(512))


class EventDetailHistory(db.Model):
    __tablename__ = 'event_detail_history'

    event_id = db.Column(db.Integer, index=True)
    detail_url = db.Column(db.String(2048))


class EventCeleryTask(db.Model):
    __tablename__ = 'event_celery_task'
    event_id = db.Column(db.Integer, unique=True, index=True)

    start_notify_task_id = db.Column(db.String(36))
    start_task_id = db.Column(db.String(36))
    end_task_id = db.Column(db.String(36))
    apply_end_task_id = db.Column(db.String(36))
    checkout_task_id = db.Column(db.String(36))


class EventTicketType(db.Model):
    __tablename__ = 'event_ticket_type'
    STATUS = {
        'draft': 0,
        'activated': 1,
        'deactivated': -1
    }
    event_id = db.Column(db.Integer, index=True)
    name = db.Column(db.String(128))
    desc = db.Column(db.TEXT)
    ticket_left_quantity = db.Column(db.Integer, default=0)
    ticket_quantity = db.Column(db.Integer)
    price = db.Column(db.Integer)

    need_audit = db.Column(db.Boolean, default=False)
    member_only = db.Column(db.Boolean, default=False)
    can_refund = db.Column(db.Boolean, default=False)

    max_buy_count = db.Column(db.Integer, default=1)
    sequence = db.Column(db.Integer, default=100)
    status = db.Column(db.SmallInteger, default=STATUS['draft'])
    # 迁移用
    m_ticket_id = db.Column(db.Integer)
    m_activity_id = db.Column(db.Integer)
    description = db.Column(db.String(128))

    @property
    def status_code(self):
        if self.status == self.STATUS['draft']:
            return 'draft'
        elif self.status == self.STATUS['online']:
            return 'online'
        elif self.status == self.STATUS['offline']:
            return 'offline'
        else:
            return 'unknown'

    def update_quantities(self):
        ticket_count = db.session.query(EventTicket.id) \
            .filter(and_(EventTicket.event_ticket_type_id == self.id,
                         EventTicket.status != EventTicket.STATUS['refund'])) \
            .count()
        self.ticket_left_quantity = self.ticket_quantity - ticket_count


class EventCustomType(db.Model):
    __tablename__ = 'event_custom_type'

    event_id = db.Column(db.Integer, index=True)
    custom_type_uuid = db.Column(db.String(32))
    name = db.Column(db.String(32))
    sequence = db.Column(db.Integer, default=100)


class EventTicketAudit(db.Model):
    __tablename__ = 'event_ticket_audit'
    STATUS = {
        'committed': 0,
        'audited': 1,
        'reject': -1
    }
    event_id = db.Column(db.Integer, index=True)
    ticket_type_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    ticket_quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Integer)
    buyer_name = db.Column(db.String(20))
    buyer_phone = db.Column(db.String(20))
    status = db.Column(db.SmallInteger, default=STATUS['committed'])

    @classmethod
    def create_audit(cls, event, ticket_type, user, params):
        ticket_audit = EventTicketAudit.query.filter_by(event_id=event.id,
                                                        ticket_type_id=ticket_type.id,
                                                        user_id=user.id,
                                                        status=EventTicketAudit.STATUS['committed']).first()
        if ticket_audit is None:
            ticket_audit = cls()
            ticket_audit.event_id = event.id
            ticket_audit.ticket_type_id = ticket_type.id
            ticket_audit.user_id = user.id
            ticket_audit.ticket_quantity = params['ticket_count']
            ticket_audit.price = ticket_type.price
            ticket_audit.buyer_name = params['name']
            ticket_audit.buyer_phone = params['phone']
            db.session.add(ticket_audit)
            db.session.commit()

        return ticket_audit


def make_order_no():
    return 'EV{0}-{1}'.format(datetime.now().strftime(TIMESTAMP),
                              generate_code_string(7, 'upper'))


class EventOrder(db.Model):
    STATUS = {
        'unpaid': 0,
        'paid': 1,
        'finished': 2,
        'canceled': -1,
        'system_canceled': -2,
        'refunding': -3,
        'refunded': -4,
        'system_refunding': -5,
        'system_refunded': -6
    }
    desc = db.Column(db.String(200))

    order_number = db.Column(db.String(50), default=make_order_no, unique=True, index=True)
    transaction_id = db.Column(db.String(32))

    event_id = db.Column(db.Integer, index=True)
    event_ticket_type_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)

    buyer_name = db.Column(db.String(512))
    buyer_phone = db.Column(db.String(32))

    price = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    amount = db.Column(db.Integer)
    status = db.Column(db.SmallInteger, default=STATUS['unpaid'])
    canceled_reason = db.Column(db.String(64))
    finished_time = db.Column(db.DateTime)
    expired_time = db.Column(db.DateTime)

    share_code = db.Column(db.String(16))
    custom_desc = db.Column(db.String(512))

    ##迁移用
    m_openid = db.Column(db.String(32))
    m_ticket_id = db.Column(db.Integer)
    m_activity_id = db.Column(db.Integer)
    m_member_id = db.Column(db.Integer)

    @property
    def status_code(self):
        if self.status == EventOrder.STATUS['unpaid']:
            return 'unpaid'
        elif self.status == EventOrder.STATUS['paid']:
            return 'paid'
        elif self.status == EventOrder.STATUS['finished']:
            return 'finished'
        elif self.status == EventOrder.STATUS['canceled']:
            return 'canceled'
        elif self.status == EventOrder.STATUS['system_canceled']:
            return 'system_canceled'
        elif self.status == EventOrder.STATUS['refunding']:
            return 'refunding'
        elif self.status == EventOrder.STATUS['refunded']:
            return 'refunded'
        else:
            return 'unknown'

    @classmethod
    def order_paid(cls, order_number, transaction_id=None):
        order = db.session.query(EventOrder).filter_by(order_number=order_number).first()
        if order is None:
            raise NotFound('Order not found')
        if order.status == cls.STATUS['unpaid']:
            event = db.session.query(Event).get(order.event_id)
            user = db.session.query(User).get(order.user_id)
            ticket_type = db.session.query(EventTicketType).get(order.event_ticket_type_id)

            for i in range(order.quantity):
                ticket = EventTicket.create_ticket(event, order, ticket_type, user)
                db.session.add(ticket)

            transaction = Transaction.create_transaction(user.id, event.user_id,
                                                         transaction_id, order.order_number,
                                                         order.amount, order.desc, "event",
                                                         True, True)
            db.session.add(transaction)
            db.session.flush()
            order.transaction_id = transaction_id
            order.status = cls.STATUS['paid']
            ticket_type.update_quantities()
            db.session.add(ticket_type)
            db.session.flush()
            event.update_quantities()
            db.session.add(event)
            db.session.flush()
            db.session.add(order)
            db.session.commit()

            record = ShareAwardRecord.get_record(order.share_code, ShareAwardRecord.RECORD_TYPES['order'],
                                                 ShareAwardRecord.BUSINESS_TYPES['event'],
                                                 order.user_id, order.id)
            if record:
                record.change_status(ShareAwardRecord.STATUS['paid'])
                db.session.add(record)
                db.session.commit()

        return order

    @classmethod
    def create_order(cls, event, ticket_type, buyer, now, params):
        order = EventOrder()
        order.event_id = event.id
        order.event_ticket_type_id = ticket_type.id
        order.user_id = buyer.id
        order.buyer_phone = params['phone']
        order.buyer_name = params['name']
        custom_data = ''
        count = 0
        for custom_info in params.get('custom_info', []):
            custom_data += custom_info.get('name') + ':' + custom_info.get('value')
            if count != len(params.get('custom_info')) - 1:
                custom_data += ','
            count = count + 1
        order.custom_desc = custom_data
        order.price = ticket_type.price
        if order.price == 0:
            order.status = EventOrder.STATUS['finished']
        order.quantity = params['ticket_count']
        order.amount = order.price * order.quantity
        order.expired_time = now + timedelta(hours=2)
        order.share_code = params.get('share_code')
        order.desc = '活动: {event} \n类型: {ticket_type}'.format(event=event.title, ticket_type=ticket_type.name)
        db.session.add(order)
        db.session.commit()

        if order.price > 0:
            ShareAwardRecord.create_record(order.share_code,
                                           ShareAwardRecord.RECORD_TYPES['order'],
                                           order.user_id, order.id)

        return order

    @property
    def publisher(self):
        return db.session.query(Event.id, UserWechat.public_openid.label('openid')) \
            .join(User, User.id == Event.user_id) \
            .join(UserWechat, UserWechat.user_id == User.id) \
            .filter(Event.id == self.event_id).first()


def make_refund_order_no():
    return 'REV{0}-{1}'.format(datetime.now().strftime(TIMESTAMP),
                               generate_code_string(7, 'upper'))


class EventUserCustomInfo(db.Model):
    __tabelname__ = 'event_user_custom_info'

    user_id = db.Column(db.Integer, index=True)
    order_id = db.Column(db.Integer, index=True)
    ticket_type_id = db.Column(db.Integer, index=True)
    custom_info_uuid = db.Column(db.String(32))
    name = db.Column(db.String(32))
    value = db.Column(db.String(32))
    sequence = db.Column(db.Integer, default=100)

    @classmethod
    def create_user_custom(cls, order_id, ticket_type_id, user_id, custom_infos):
        if not custom_infos:
            return

        for custom_info in custom_infos:
            custom_type = CustomType.query.filter_by( \
                    uuid=custom_info['custom_type_uuid']).first()
            user_custom_info = cls()
            user_custom_info.user_id = user_id
            user_custom_info.order_id = order_id
            user_custom_info.ticket_type_id = ticket_type_id
            user_custom_info.custom_info_uuid = custom_info['custom_type_uuid']
            user_custom_info.name = custom_info['name']
            user_custom_info.value = custom_info['value']
            user_custom_info.sequence = custom_type.sequence
            db.session.add(user_custom_info)

        db.session.commit()


class EventTicketRefundOrder(db.Model):
    __tablename__ = 'event_ticket_refund_order'
    STATUS = {
        'applying': 0,
        'refunding': 1,
        'success': 2,
        'failed': -1,
        'refused': -2,
    }
    refund_no = db.Column(db.String(25), default=make_refund_order_no, unique=True, index=True)
    transaction_id = db.Column(db.String(32))

    event_id = db.Column(db.Integer, index=True)
    event_order_id = db.Column(db.Integer, index=True)
    event_ticket_type_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    # optional
    event_ticket_id = db.Column(db.Integer, index=True)

    refund_fee = db.Column(db.Integer)

    apply_reason = db.Column(db.String(200))
    desc = db.Column(db.String(200))
    failed_reason = db.Column(db.String(200))
    end_time = db.Column(db.DateTime)

    status = db.Column(db.SmallInteger, default=STATUS['applying'])

    @property
    def status_code(self):
        if self.status == EventTicketRefundOrder.STATUS['applying']:
            return 'applying'
        elif self.status == EventTicketRefundOrder.STATUS['refunding']:
            return 'refunding'
        elif self.status == EventTicketRefundOrder.STATUS['refused']:
            return 'refused'
        elif self.status == EventTicketRefundOrder.STATUS['success']:
            return 'success'
        elif self.status == EventTicketRefundOrder.STATUS['failed']:
            return 'failed'
        else:
            return 'unknown'

    @property
    def refund_username(self):
        return UserWechat.query.filter_by(user_id=self.user_id).first().nickname

    @classmethod
    def create_refund(cls, order, reason):
        refund_order = cls()
        refund_order.event_order_id = order.id
        refund_order.event_id = order.event_id
        refund_order.event_ticket_type_id = order.event_ticket_type_id
        refund_order.user_id = order.user_id
        refund_order.refund_fee = order.amount
        refund_order.apply_reason = reason
        refund_order.desc = order.desc
        db.session.add(refund_order)
        db.session.commit()
        return refund_order

    @classmethod
    def task_create_refund(cls, order, reason):
        refund_order = cls()
        refund_order.event_order_id = order.id
        refund_order.event_id = order.event_id
        refund_order.event_ticket_type_id = order.event_ticket_type_id
        refund_order.user_id = order.user_id
        refund_order.refund_fee = order.amount
        refund_order.apply_reason = reason
        refund_order.desc = order.desc

        return refund_order

    @classmethod
    def refund_success(cls, refund_order_no, transaction_id):
        refund_order = EventTicketRefundOrder.query.filter_by(refund_no=refund_order_no).first()
        if refund_order and refund_order.status == cls.STATUS['refunding']:
            event_order = db.session.query(Event.user_id) \
                .join(EventOrder, EventOrder.event_id == Event.id) \
                .filter(EventOrder.id == refund_order.event_order_id).first()
            transaction = Transaction.create_transaction(event_order.user_id, refund_order.user_id,
                                                         transaction_id, refund_order.refund_no,
                                                         refund_order.refund_fee, refund_order.desc, "refund",
                                                         False, False)

            order = EventOrder.query.get(refund_order.event_order_id)
            if order.status == EventOrder.STATUS['system_refunding']:
                order.status = EventOrder.STATUS['system_refunded']
            else:
                order.status = EventOrder.STATUS['refunded']
            db.session.add(order)
            db.session.flush()
            if refund_order.event_ticket_id:
                event_ticket = EventTicket.query.get(refund_order.event_ticket_id)
                event_ticket.status = EventTicket.STATUS['refund']
                db.session.add(event_ticket)
                db.session.flush()
            else:
                event_tickets = EventTicket.query.filter_by(buyer_id=refund_order.user_id,
                                                            event_id=refund_order.event_id,
                                                            event_order_id=order.id).all()
                for item in event_tickets:
                    item.status = EventTicket.STATUS['refund']
                    db.session.add(item)
                    db.session.flush()

            ticket_type = db.session.query(EventTicketType).get(refund_order.event_ticket_type_id)
            event = Event.query.get(refund_order.event_id)
            db.session.add(transaction)
            db.session.flush()
            refund_order.transaction_id = transaction.id
            refund_order.status = cls.STATUS['success']
            ticket_type.update_quantities()
            db.session.add(ticket_type)
            db.session.flush()
            event.update_quantities()
            db.session.add(event)
            db.session.flush()

            """对于报名渠道带有分享码的同学，退款后，分享码所有者的奖励要取消掉"""
            share_award_record = db.session.query(ShareAwardRecord).filter_by(order_id=order.id).first()
            if share_award_record:
                share_award_record.status = ShareAwardRecord.STATUS['refund']
                db.session.add(share_award_record)
                db.session.flush()

            db.session.add(refund_order)
            db.session.commit()

        return refund_order


class EventTicket(db.Model):
    __tablename__ = 'event_ticket'
    STATUS = {
        'unused': 0,
        'used': 1,
        'expired': 2,  # TODO: add a cron job to change ticket status
        'refunding': -1,
        'refund': -2
    }
    ticket_number = db.Column(db.String(32))
    event_title = db.Column(db.String(128))
    ticket_type_name = db.Column(db.String(128))
    # 买票人
    buyer_id = db.Column(db.Integer, index=True)  # , nullable=False
    # 参加活动成员, default = buyer_id
    holder_id = db.Column(db.Integer, index=True)
    holder_name = db.Column(db.String(512))
    holder_phone = db.Column(db.String(24))
    bind = db.Column(db.Boolean, default=False)  # bind = True can not change member_id

    price = db.Column(db.Integer)
    status = db.Column(db.SmallInteger, default=STATUS['unused'])
    _can_refund = db.Column(db.Boolean, default=False)
    # 活动开始时间
    event_start_at = db.Column(db.DateTime)
    event_end_at = db.Column(db.DateTime)

    event_id = db.Column(db.Integer, index=True)
    event_order_id = db.Column(db.Integer, index=True)
    event_refund_order_id = db.Column(db.Integer, index=True)
    event_ticket_type_id = db.Column(db.Integer, index=True)

    # 迁移用
    m_openid = db.Column(db.String(32))
    m_activity_id = db.Column(db.Integer)
    m_ticket_id = db.Column(db.Integer)
    m_number = db.Column(db.Integer)
    m_order_no = db.Column(db.String(32))
    m_member_id = db.Column(db.Integer)

    @property
    def can_refund(self):
        if self.price == 0:
            return False
        if datetime.now() >= self.event_start_at:
            return False
        if self._can_refund and self.status == EventTicket.STATUS['unused']:
            return True
        return False

    @classmethod
    def gen_ticket_no(cls, dt):
        return 'T{0}{1}'.format(dt.strftime('%y%Y%m%d%H%M'), generate_code_string(4, 'upper'))

    @classmethod
    def create_ticket(cls, event, order, ticket_type, buyer):
        ticket = cls()
        ticket.event_id = event.id
        ticket.event_start_at = event.start_at
        ticket.event_end_at = event.end_at

        ticket.event_order_id = order.id
        ticket.event_ticket_type_id = ticket_type.id

        ticket.buyer_id = buyer.id
        ticket.holder_id = buyer.id
        ticket.holder_name = order.buyer_name
        ticket.holder_phone = order.buyer_phone

        ticket.price = order.price
        ticket._can_refund = ticket_type.can_refund

        ticket.event_title = event.title
        ticket.ticket_type_name = ticket_type.name
        ticket.ticket_number = cls.gen_ticket_no(ticket.event_start_at)

        return ticket

    def change_member(self, member):
        pass


class EventView(db.Model):
    __tablename__ = 'event_view'
    event_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    # 迁移用
    m_openid = db.Column(db.String(32))


class EventViewStatistic(db.Model, BaseUserAgent):
    __tablename__ = 'event_view_statistic'
    event_id = db.Column(db.Integer, index=True)
    user_id = db.Column(db.Integer, index=True)
    event_view_id = db.Column(db.Integer, index=True)
    # 迁移用
    m_openid = db.Column(db.String(32))
    m_activity_id = db.Column(db.Integer, index=True)
