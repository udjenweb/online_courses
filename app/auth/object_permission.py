# coding: utf-8
from .models import User
from tools.eve.auth import (
    PERMISSION_READ,        # read all and edit self
    PERMISSION_EDIT,        # modify all data, but cen not delete
    PERMISSION_DELETE,      # delete
)


def check_permission(user, model, action_type, data):

    # TODO запретить доступ на чтение к некоторым полям
    # проще в реквест подкидывать фильтр что бы отдовать не все объекты
    # * еще как бы отдовать разное количество полей
    #   к примеру мыло владельцу показывае а другим нет
    #   или рейтинг по книгам - как то динамически модифицировать схему ресурса

    # allow all users read
    if action_type in [PERMISSION_READ, ]:
        return True

    # only own record can edit or deleted
    if action_type in [PERMISSION_EDIT, PERMISSION_DELETE, ]:
        if user.id == data['_id']:
            return True



