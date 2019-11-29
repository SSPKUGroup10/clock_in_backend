# -*- coding:utf-8 -*-
from random import Random
from urllib.parse import urlparse
from os import path
from urllib.request import urlopen
from shutil import copyfileobj
from .datetime import NORMAL_DATETIME, str2datetime, ISO_DATETIME, TIMESTAMP, monthdelta, utc_datetime, \
    CN_DATETIME_FORMAT
from .exception import BusinessError
from .resource import CommonResource
from .schema import *
from .interfaces import ItemInterface, ListInterface
from .decorator import api, response_json
from .xml import dict_to_xml

DATA_BASE_PATH = 'init_data/statics'

CELLPHONE_PATTERN = '[^\._-][\w\.-]+@(?:[A-Za-z0-9]+\.)+[A-Za-z]+$|^0\d{2,3}\d{7,8}$|^1[3456789]\d{9}$'

CHARTYPES = {
    'number': '0123456789',
    'lower': '0123456789abcdefghijklmnopqrstuvwxyz',
    'upper': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'lower_only': 'abcdefghijklmnopqrstuvwxyz',
    'upper_only': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'alpha': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    'all': '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
}


def generate_code_string(random_length=6, char_type='number'):
    code = ''
    chars = CHARTYPES.get(char_type) or '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        code += chars[random.randint(0, length)]
    return code


def download_file(url):
    try:
        print('downloading:', url)
        a = urlparse(url)
        filename = path.basename(a.path)
        filename = 'temp/{0}_{1}'.format(generate_code_string(10), filename)
        with urlopen(url, timeout=5) as response, open(filename, 'wb') as out_file:
            copyfileobj(response, out_file)
        return filename
    except Exception as e:
        print(url, e)
        return None
