# coding: utf-8
import logging
from flask import current_app
from werkzeug.exceptions import HTTPException, Conflict
from sqlalchemy.exc import IntegrityError
from config import (
    ROLE_GUEST,
    ROLE_USER
)

log = logging.getLogger(__name__)


def register_new_user(email, password, role=ROLE_USER, **kwargs):
    session = current_app.data.driver.session

    from .models import User
    from ..acl.models import Role
    try:
        role = session.query(Role).filter_by(name=role).one()
        user = User(email=email, password=password, **kwargs)
        user.roles = [role, ]
        session.add(user)
        user.session.commit()

    except IntegrityError:
        session.rollback()
        raise Conflict('current email "{email}" already in use.'.format(email=email))
    # todo: add registration handling
    return user


