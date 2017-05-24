# coding: utf-8
from sqlalchemy import func
from sqlalchemy import (
    Column, String, Integer, DateTime,
)
from ..aditional.property import classproperty
from eve_sqlalchemy.decorators import registerSchema
from eve.methods.common import resolve_document_etag

from datetime import datetime
from sqlalchemy.orm import validates


def datetime_now_eve_format():
    return datetime.utcnow().replace(microsecond=0)  # like do it Eve in his methods


def create_EveMixin(etag_name):
    ETAG_NAME = etag_name

    # base model for eve
    class EveMixinBase:
        __abstract__ = True

        _id = Column(Integer, primary_key=True, autoincrement=True)
        _created = Column(DateTime, default=func.now())
        _updated = Column(DateTime, default=func.now(), onupdate=func.now())

        # about _id / id
        # http://eve-sqlalchemy.readthedocs.io/en/0.3/tutorial.html#start-eve
        # https://github.com/RedTurtle/eve-sqlalchemy/issues/52
        # https://github.com/RedTurtle/eve-sqlalchemy/issues/99

        @classproperty
        def resource_name(obj, cls):
            return cls.__tablename__

        @classproperty
        def _eve_schema(obj, cls):
            """auto creator eve schema"""
            schema_name = cls.resource_name
            registerSchema(schema_name)(cls)
            # *!* modify standard access point
            cls._eve_schema = cls._eve_schema[schema_name]

            # protect Eve-API for modify by clients app
            # * rows _created, _updated, _etag protected by Eve, and not add to schema access.
            cls._eve_schema['schema']['_id'].update({'readonly': True})

            return cls._eve_schema

        @staticmethod
        def calc_etag(context):
            document = dict(context.current_parameters)
            document.pop(ETAG_NAME, None)
            resolve_document_etag(documents=[document])
            return document[ETAG_NAME]

        def set_etag(self, etag):
            self.__setattr__(ETAG_NAME, etag)

        def get_etag(self):
            return getattr(self, ETAG_NAME)

    setattr(EveMixinBase, ETAG_NAME, Column(String, default=EveMixinBase.calc_etag))

    return EveMixinBase

