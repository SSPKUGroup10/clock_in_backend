# -*- coding:utf-8 -*-
from .daemon import CronDaemon
from .conf import PID_FILE, MYSQL_CONN, ENV

daemon = CronDaemon(PID_FILE, MYSQL_CONN, ENV)


def restart():
    daemon.restart()


def stop():
    daemon.stop()
