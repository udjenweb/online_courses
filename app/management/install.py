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
    ALL_ROLES,
    ROLE_GUEST, ROLE_ROOT,
)
from ..auth.models import User
from ..acl.models import Role, Permission, Resource, UserAssignment
from ..auth.register import register_new_user, Conflict
from ..resources import get_domains
from .install_online_courses import InstallOnlineCoursesCommand


log = logging.getLogger(__name__)


class InstallCommand(Command):
    """install basic roles for drive of system"""
    def run(self):
        db = current_app.data.driver

        # add roles:
        print(draw.header('add roles'))
        print("default roles: {}".format(draw.array(ALL_ROLES, inline=True)))
        buck_insert_or_pass(Role, [{'name': role} for role in ALL_ROLES])

        # add resources
        print(draw.header('add resources'))
        domains = get_domains()
        resources = list([name for name in domains])
        print("resources: {}".format(draw.array(resources, inline=True)))
        buck_insert_or_pass(Resource, [{'name': resource} for resource in resources])

        # add permissions
        print(draw.header('create all permission for root-role to all resources'))
        print("permissions: {}".format(draw.array(PERMISSION_ALL, inline=True)))
        root_role = Role.where(name=ROLE_ROOT).first()

        def permissions():
            for resource in Resource.all():
                for action in PERMISSION_ALL:
                    yield {'action': action,
                           'role_id': root_role._id,
                           'resource_id': resource._id,
                           'for_all_objects': True
                           }
        buck_insert_or_pass(Permission, list(permissions()))

        # доступ к user модели
        def permissions():
            resource = Resource.where(name=domains.get_name(User)).first()
            for role in Role.all():
                for action in PERMISSION_ALL:
                    yield {'action': action,
                           'role_id': role._id,
                           'resource_id': resource._id,
                           'for_all_objects': False
                           }
        buck_insert_or_pass(Permission, list(permissions()))

        print(draw.header('create new user'))
        user_data = {'email': 'root', 'password': 'root', 'role': ROLE_ROOT}
        print("permissions: {}".format(draw.array(user_data, inline=True)))
        try:
            root_user = register_new_user(**user_data)
        except Conflict as exc:
            root_user = User.query.filter_by(email=user_data['email']).first()
            print(draw.color('WARNING:  {error}!'.format(error=exc.get_description()), 'RED'))
            if confirm('    Change password for root user?'):
                new_password = prompt('    enter new password, default:', default='root')
                root_user.password = new_password
                root_user.session.commit()
                print("    [!] password wos changed to: '{}' ".format(new_password))
            else:
                print('    password wos NOT changed.')

        print(draw.header("assignment role '{role_name}' to user '{user_email}'"
                          "".format(role_name=ROLE_ROOT, user_email=root_user.email)))
        try:
            UserAssignment.create(role_id=root_role._id, user_id=root_user._id)
        except (sqlalchemy.exc.IntegrityError, psycopg2.IntegrityError):
            pass
        print('ok.')

        print(draw.header('InstallOnlineCoursesCommand'))
        InstallOnlineCoursesCommand().run()

        print(draw.header('end.'))



