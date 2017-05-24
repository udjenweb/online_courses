# coding: utf-8
from abc import ABCMeta, abstractclassmethod


class CurrentObject(metaclass=ABCMeta):
    @abstractclassmethod
    def _get_instance(self):
        """redefined method must return instance"""

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            instance = self._get_instance()
            return getattr(instance, key)

    def __call__(self, *args, **kwargs):
        instance = self._get_instance()
        return instance


class ProxyObject(metaclass=ABCMeta):
    @abstractclassmethod
    def _get_instance(self):
        """redefined method must return instance"""

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            instance = self._get_instance()
            return getattr(instance, key)


