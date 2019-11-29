# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from app.models.event import Event


def update_event_status(db):
    with db.db.get_session() as session:
        now = datetime.now()
        events = session.query(Event) \
            .filter(Event.status == Event.STATUS['audited'], Event.timing_status != Event.TIMING_STATUS['closed'])
        for event in events:
            if event.apply_end_at is None:
                event.apply_end_at = event.start_at
            print('event {event.title}: {event.start_at}-{event.end_at}, {event.status_code}'.format(event=event))
            if event.apply_end_at < now < event.start_at:
                event.timing_status = Event.TIMING_STATUS['preparing']
            if event.end_at < now and event.timing_status != Event.TIMING_STATUS['finished']:
                event.timing_status = Event.TIMING_STATUS['finished']
            if event.start_at < now < event.end_at and event.timing_status != Event.TIMING_STATUS['ongoing']:
                event.timing_status = Event.TIMING_STATUS['ongoing']
            session.add(event)

        session.commit()


def event_checkout(db, prod):
    with db.db.get_session() as session:
        query = session.query(Event).filter()
