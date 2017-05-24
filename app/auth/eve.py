# coding: utf-8
import logging
import eve.auth
from .user_instance import current_user, Unauthorized

from tools.eve.auth import PERMISSION_REQUESTS, PERMISSION_ADD
from tools.aditional.console.sqlparse import fsql
from flask import current_app, request
from .object_permission_checker import checker as object_permission_checker

log = logging.getLogger(__name__)


class BasicAuth(eve.auth.BasicAuth):
    def authorized(self, allowed_roles, resource, method):
        """ Validates the the current request is allowed to pass through."""
        username, password = '', ''
        return self.check_auth(username, password, allowed_roles, resource, method)

    # check if user is authorized [True/False]
    def check_auth(self, username, password, allowed_roles, resource, method):

        if not resource:
            return True

        try:
            user = current_user()
            self.set_request_auth_value(user._id)  # owner of data
        except Unauthorized:
            return False  # DENY ACCESS for NOT authorized users

        action_type = PERMISSION_REQUESTS[method]

        # seep 1
        # access control for RESOURCE
        from .models import User
        from ..acl.models import UserAssignment, Permission, Resource

        # список ролей должен быть загруже в оперативную память - добавить расшерение для ролей
        #   но как быть если роли обновляются? надо обновлять и список!
        # TODO make optimization for sql-auth-request
        result = current_app.data.driver.session.query(Permission._id)\
            .select_from(User)\
            .filter(User._id == user._id)\
            .join(UserAssignment, UserAssignment.user_id == User._id) \
            .join(Permission, UserAssignment.role_id == Permission.role_id)\
            .filter(Permission.action == action_type)\
            .join(Resource, Permission.resource_id == Resource._id)\
            .filter(Resource.name == resource)  # TODO: may be collision with install script
        # print(fsql(result))
        if result.count() < 1:
            return False

        # allow access for administration of website
        if result.filter(Permission.for_all_objects == True).count() > 0:
            return True

        # seep 2
        # access control for OBJECT
        checkers_list = []

        from .object_permission import check_permission as user_model_check_permission
        from .models import User
        checkers_list.append((user_model_check_permission, [
            User,
        ]))

        from ..online_courses.object_permission import check_permission as online_courses_permission
        from ..online_courses.models import Specialization, TeacherSpecialization, Class, StudentInClass
        checkers_list.append((online_courses_permission, [
            Specialization, TeacherSpecialization, Class, StudentInClass,
        ]))

        return object_permission_checker(
            checkers_list,
            user,
            resource,
            action_type,
            request.json  # this parameter can be changed at any checkers!
        )


