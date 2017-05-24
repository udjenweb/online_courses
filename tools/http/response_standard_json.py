# coding: utf-8
from flask import make_response, jsonify
"""
    compatibility one standard for eve and flask
"""

# settings for eve
RESPONSE_STATUS = '_status'
RESPONSE_ERROR = '_error'
RESPONSE_STATUS_ERROR = 'ERR'
RESPONSE_STATUS_OK = 'OK'


# request-wrapper for flask
def response_data_success(data=None, status=200):
    data = data if data else {}
    assert isinstance(data, dict)
    data.update({
        RESPONSE_STATUS: RESPONSE_STATUS_OK
    })
    return make_response(jsonify(data), status)


def response_data_error(message, data=None, status=400):
    data = data if data else {}
    data.update({
        RESPONSE_STATUS: RESPONSE_STATUS_ERROR,
        RESPONSE_ERROR:  {
            'code': status,
            'message': message,
        }
    })
    return make_response(jsonify(data), status)

