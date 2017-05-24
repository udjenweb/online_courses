# coding: utf-8
from werkzeug.exceptions import Unauthorized
from flask import g
from flask import request
from functools import wraps

from tools import CurrentObject


def _set_session_user(user):
    g._current_user = user


def _get_session_user():
    user = g.get('_current_user', None)
    return user


def authorize_user(user):
    from .token_manage import generate_access_token
    token_data = {
        'email': user.email,
        'password': user.password  # invalid jwt if user changed password (it's only hash of password)
    }
    user_access_token = generate_access_token(token_data)

    _set_session_user(user)
    return user_access_token


def get_current_user():
    user = _get_session_user()
    if user:
        return user
    from .models import User

    if request.authorization and request.authorization.type == 'basic':
        email = request.authorization.username
        password = User.encrypt(request.authorization.password)
    else:
        from .token_manage import get_access_token, parse_access_token
        access_token, token_type = get_access_token()
        if token_type != 'Bearer':
            raise Unauthorized('invalid type of access token.')
        # todo: add handling for authorization by Basic-key (encoding: base64 <login:password>)
        token_data = parse_access_token(access_token)
        email = token_data['email']
        password = token_data['password']

    user = User.query.filter_by(email=email).first()
    if not user:
        raise Unauthorized('invalid access token.')
    if user.password != password:  # invalid jwt if user changed password (it's only hash of password)
        raise Unauthorized('invalid access token.')

    _set_session_user(user)
    return user


class CurrentUser(CurrentObject):
    def _get_instance(self):
        user = get_current_user()
        return user

current_user = CurrentUser()


def user_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        result = f(*args, user=user, **kwargs)
        return result
    return wrapper

