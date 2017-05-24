# coding: utf-8
import logging
from flask import current_app
from flask_script import Command, prompt
import sqlalchemy
import psycopg2
from tools import draw
from ..management.tools import warning, error, confirm, buck_insert_or_pass

from config import (
    LOCAL_PROVIDER_NAME,
    PERMISSION_ALL,
PERMISSION_ADD,
PERMISSION_READ,
PERMISSION_DELETE,
PERMISSION_EDIT,
    ALL_ROLES,
    ROLE_GUEST, ROLE_ROOT,
    ROLE_TEACHER, ROLE_STUDENT
)
from ..auth.models import User
from ..acl.models import Role, Permission, Resource, UserAssignment
from ..auth.register import register_new_user, Conflict
from ..resources import get_domains
from ..online_courses.models import Specialization, TeacherSpecialization, Class, StudentInClass


log = logging.getLogger(__name__)


class InstallOnlineCoursesCommand(Command):
    """install basic roles for drive of system"""
    def run(self):
        db = current_app.data.driver
        #
        #

        def permissions():
            domains = get_domains()
            resources = [
                domains.get_name(Specialization),
                domains.get_name(TeacherSpecialization),
                domains.get_name(Class),
                domains.get_name(StudentInClass),
            ]

            for role in Role.where(name__in=[ROLE_STUDENT, ROLE_TEACHER]).all():
                print('role', role, role.name)
                for resource in Resource.where(name__in=resources).all():
                    print('resource', resource)

                    # учитель
                    #   специализация:  читать, добавить
                    #   у-с:            читать, добавить удалить обновить
                    #   класс:          читать, добавить удалить обновить (все *)
                    #
                    if role.name == ROLE_TEACHER:

                        if resource.name == domains.get_name(Specialization):
                            for action in [PERMISSION_READ, PERMISSION_ADD]:
                                yield {'action': action, 'role_id': role._id, 'resource_id': resource._id,
                                       'for_all_objects': False}

                        elif resource.name == domains.get_name(TeacherSpecialization):
                            for action in PERMISSION_ALL:
                                yield {'action': action, 'role_id': role._id, 'resource_id': resource._id,
                                       'for_all_objects': False}

                        elif resource.name == domains.get_name(Class):
                            for action in PERMISSION_ALL:
                                yield {'action': action, 'role_id': role._id, 'resource_id': resource._id,
                                       'for_all_objects': False}

                    # ученик:
                    #   класс:          читать
                    #   специализация:  читать
                    #   у-к:            читать, добавить удалить обновить (все *)
                    #
                    elif role.name == ROLE_STUDENT:

                        if resource.name == domains.get_name(Class):
                            for action in [PERMISSION_READ]:
                                yield {'action': action, 'role_id': role._id, 'resource_id': resource._id,
                                       'for_all_objects': False}

                        elif resource.name == domains.get_name(Specialization):
                            for action in [PERMISSION_READ]:
                                yield {'action': action, 'role_id': role._id, 'resource_id': resource._id,
                                       'for_all_objects': False}

                        elif resource.name == domains.get_name(StudentInClass):
                            for action in PERMISSION_ALL:
                                yield {'action': action, 'role_id': role._id, 'resource_id': resource._id,
                                       'for_all_objects': False}

        #
        permission_list = list(permissions())
        print(draw.array(permission_list))
        buck_insert_or_pass(Permission, permission_list)

