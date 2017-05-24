# coding: utf-8
import logging
from flask import current_app
from flask_script import Command, prompt
from tools import draw

import sqlalchemy
import psycopg2


log = logging.getLogger(__name__)

warning = lambda text: draw.color('WARNING: ' + text, 'YELLOW')
error = lambda text: draw.color('ERROR: ' + text, 'RED')
info = lambda text: draw.color('INFO: ' + text, draw.GREEN)


def confirm(message, default='No'):
    while True:
        note = draw.color("(pleas enter'Yes' or 'No') default", )
        response = prompt("{message}{note}".format(message=message, note=note), default=default)
        if response in ['y', 'yes', ]:
            return True
        if response in ['n', 'no', 'not', ]:
            return False


def buck_insert_or_pass(model, items):
    session = current_app.data.driver.create_scoped_session()
    for item in items:
        try:
            session.add(model(**item))
            session.commit()
            print(info('added:'), draw.color(item, 'WHITE'))
        except (sqlalchemy.exc.IntegrityError, psycopg2.IntegrityError):
            print(warning("already exists {} {} (ignored)".format(model, draw.color(item, 'WHITE'))))
            session.rollback()
    session.close()

