# -*- coding:utf-8 -*-


YOOQUN_ERRORS = {
    'APITimingError': [60001, 'API调用时序错误'],
    'FieldIncomplete': [60002, '字段缺失错误'],
    'APICallError': [60003, 'API调用错误，该用户不应该调用该API'],
    'OrderUnPaid': [60004, '订单尚未支付'],
    'SmsCodeError': [60005, '短信验证码错误'],
    'DataRelationError': [60006, '数据归属错误'],
    'UserAuthError': [60007, '用户无权限'],
    'DataNotFound': [60008, '数据不存在'],
    'MethodNotSupport': [60009, '不支持该方法'],
    'DuplicateError': [60010, '数据不允许重复'],
    'DataNotAllowed': [60011, '数据不被允许'],
    'FakeDataError': [60012, '数据造假'],
    'EventError': [60013, '活动相关错误'],
    'TicketTypeError': [60014, '票种相关错误'],
    'WithdrawNotHandle': [60015, '有未处理的提现申请'],
    'WithdrawAmountError': [60016, '提现金额与账户可提现金额不符'],
    'AuditHandled': [60017, '该条审核申请已经处理过']
    # 60002: '子数据不属于待处理数据',
    # 60003: '输入参数错误，详见errMsg',
    # 60004: 'API调用错误，后台逻辑不允许调用',
    # 60005: '不支持该方法',
    # 60006: '字段没有填写完整',
    # 60007: '非法操作，归属错误',
    # 60008: '该手机号码已经绑定其他用户，请换一个手机号码重试',
    # 60009: '验证码校验失败'
}
