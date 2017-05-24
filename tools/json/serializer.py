# coding: utf-8
from datetime import datetime


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return serial
    # raise TypeError("Type not serializable")
    return str(obj)

