# coding: utf-8
import flask_sqlalchemy
from eve_sqlalchemy import SQL
from flask import current_app
from flask import abort
from functools import wraps
import psycopg2
import sqlalchemy
import re

from sqlalchemy_mixins import AllFeaturesMixin

from config import ETAG
from tools.eve.model import create_EveMixin
from tools.sqlalchemy.postgres import add_trigger
from sqlalchemy_mixins.utils import classproperty


class _Base(AllFeaturesMixin, flask_sqlalchemy.Model, create_EveMixin(ETAG)):
    @classproperty
    def _session(cls):  # for AllFeaturesMixin->ActiveRecordMixin->SessionMixin
        return current_app.data.driver.session

    __triggers__ = []

    @staticmethod
    def add_trigger(statement):
        trigger = add_trigger(statement)
        _Base.__triggers__.append(trigger)
        return trigger


def db_deny_update(cls):
    cls.add_trigger("""\
        CREATE TRIGGER {t}__deny_update 
            BEFORE UPDATE
            ON {t} FOR EACH ROW
        BEGIN
            RAISE EXCEPTION '{t} cen not be changed' USING ERRCODE='P0405';
        END;\
        """.format(t=cls.__tablename__))
    return cls


db = flask_sqlalchemy.SQLAlchemy(model_class=_Base)


def try_catch_wrapper(code=None, abort_message=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except (sqlalchemy.exc.IntegrityError, psycopg2.IntegrityError) as ex:
                error_code = str(ex.orig.pgcode)
                abort(403, "{}".format('IntegrityError'))  # Forbidden
            except (sqlalchemy.exc.InternalError, psycopg2.InternalError) as ex:
                error_code = str(ex.orig.pgcode)

                if error_code == 'P0405':
                    abort(405)  # default eve response : "The method is not allowed for the requested URL."

                if error_code == 'P0403':
                    source_error_message = str(ex.orig.pgerror)
                    mask = re.compile("""
                                         (?P<type>^\w*) 
                                         (?:[:]\s*)
                                         (?P<massage>.*$) 
                                      """, flags=re.MULTILINE | re.VERBOSE)
                    result = mask.findall(source_error_message)
                    if len(result) != 2:
                        raise
                    error_message = result[0][1]
                    error_context = result[1][1]
                    abort(403, "{}".format(error_message))  # Forbidden
                raise
        return wrapper
    return decorator


class SqlAlchemyDataLayer(SQL):
    driver = db

    @try_catch_wrapper()
    def insert(self, *args, **kwargs):  # PATCH
        return super(SqlAlchemyDataLayer, self).insert(*args, **kwargs)

    @try_catch_wrapper()
    def update(self, *args, **kwargs):  # PATCH
        return super(SqlAlchemyDataLayer, self).update(*args, **kwargs)

    @try_catch_wrapper()
    def replace(self, *args, **kwargs):  # PUT
        return super(SqlAlchemyDataLayer, self).replace(*args, **kwargs)

    @try_catch_wrapper()
    def remove(self, *args, **kwargs):  # PATCH
        return super(SqlAlchemyDataLayer, self).remove(*args, **kwargs)

