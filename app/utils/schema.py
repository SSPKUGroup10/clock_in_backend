# -*- coding:utf-8 -*-
from marshmallow import Schema

ERROR_MESSAGES = {
    'required': '必填字段',
    'type': '类型错误',
    'null': '输入不能为空'
}

ERROR_MESSAGES_INT = ERROR_MESSAGES.copy()
ERROR_MESSAGES_INT.update({'invalid': '输入必须为整型'})

ERROR_MESSAGES_STR = ERROR_MESSAGES.copy()
ERROR_MESSAGES_STR.update({'invalid': '输入必须为字符型'})

ERROR_MESSAGES_BOOL = ERROR_MESSAGES.copy()
ERROR_MESSAGES_BOOL.update({'invalid': '输入必须为布尔型'})


class StrictSchema(Schema):
    class Meta:
        strict = True
