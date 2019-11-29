# -*- coding:utf-8 -*-
from datetime import datetime, timedelta
from calendar import monthrange

TIMESTAMP = '%Y%m%d%H%M%S'
ISO_DATETIME = '%Y-%m-%d %H:%M:%S'
NORMAL_DATETIME = '%Y-%m-%d %H:%M:%S'
CN_DATETIME_FORMAT = '%m月%d日 %H时%M分'
PAGE_FORMAT = '%Y年%m月%d日 %H时%M分%S秒'


def str2datetime(datetime_str):
    return datetime.strptime(datetime_str, NORMAL_DATETIME)


def monthdelta(the_day, month_count):
    year = the_day.year
    month = the_day.month
    days = 0
    for i in range(0, month_count):
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        result = monthrange(year, month)
        days += result[1]
    return timedelta(days=days)


def utc_datetime(dt):
    timestamp = dt.timestamp()
    return datetime.utcfromtimestamp(timestamp)
