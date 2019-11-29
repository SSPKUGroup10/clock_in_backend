# -*- coding:utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as BaseSession, sessionmaker


class Session(BaseSession):

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


class DatabaseWrapper(object):
    def __init__(self, Session):
        self.Session = Session
        self._worker_session = None

    def get_session(self):
        return self.Session()

    @property
    def session(self):
        if self._worker_session is None:
            self._worker_session = self.Session()
        return self._worker_session

    def close(self):
        if self._worker_session:
            self._worker_session.close()


class DbConnect:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine, class_=Session)
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = DatabaseWrapper(self.Session)
        return self._db
