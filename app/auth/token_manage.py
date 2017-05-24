# coding: utf-8
import logging
from werkzeug.exceptions import Unauthorized
from flask import request
from flask import current_app
import jwt
import datetime
from jwt.exceptions import DecodeError

log = logging.getLogger(__name__)


def get_access_token():
    """
        get access token from authorization header
    :return:
        tuple: (access_token, token_type)
    """
    try:
        data = request.headers['Authorization']
    except KeyError:
        raise Unauthorized('Missing authorization header')
    token_type, access_token = str(data).split()
    return access_token, token_type


def generate_access_token(data, expiry_days=30):
    secret = current_app.config['SECRET_KEY']
    wjt_data = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=expiry_days),
        'data': data,
    }
    jwt_key = jwt.encode(wjt_data, secret)
    return jwt_key


def parse_access_token(token):
    secret = current_app.config['SECRET_KEY']
    try:
        data = jwt.decode(token, secret)
    except DecodeError:
        raise Unauthorized('invalid type of access token.')
    return data['data']

