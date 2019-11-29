# -*- coding:utf-8 -*-
import time
import schedule
from .utils import Daemon, DbConnect
from .jobs import update_event_status


class CronDaemon(Daemon):
    def __init__(self, pid, db_url=None, env='dev'):
        super().__init__(pid)
        self.db = DbConnect(db_url=db_url)
        self.prod = True if env == 'prod' else False

    def run(self):
        if self.prod:
            schedule.every(15).minutes.do(update_event_status, db=self.db)
        else:
            schedule.every(15).minutes.do(update_event_status, db=self.db)
        while True:
            schedule.run_pending()
            time.sleep(1)
