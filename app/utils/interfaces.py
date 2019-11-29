# -*- coding:utf-8 -*-
from abc import abstractclassmethod
from .exception import BusinessError


class ItemInterface:
    @abstractclassmethod
    def get(self):
        pass

    @abstractclassmethod
    def delete(self):
        pass

    @abstractclassmethod
    def update(self, **kwargs):
        pass

    def exe_update_method(self, **kwargs):
        if kwargs is None:
            raise BusinessError('API Error', 'loss params', 400)
        if not hasattr(self, kwargs.get('method')):
            raise BusinessError('APP Error', 'not support method:{0}'.format(kwargs.get('method')), 400)
        method = kwargs.get('method')
        kwargs.pop('method')
        return getattr(self, method)(**kwargs)

    @classmethod
    def check_fields(cls, schema_cls, obj):
        error_fields = []
        result = schema_cls().dump(obj).data
        for key, value in result.items():
            if value is None:
                error_fields.append(key)
        if len(error_fields):
            raise BusinessError('Fields Incomplete Error', str(error_fields), 60006)


class ListInterface:
    @abstractclassmethod
    def get(self, **kwargs):
        pass

    @abstractclassmethod
    def create(self, **kwargs):
        pass
