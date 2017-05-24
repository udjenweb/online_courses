# coding: utf-8
from .models import Specialization, TeacherSpecialization, Class, StudentInClass
from tools.eve.auth import (
    PERMISSION_ADD,
    PERMISSION_READ,        # read all and edit self
    PERMISSION_EDIT,        # modify all data, but cen not delete
    PERMISSION_DELETE,      # delete
)
from config import (
    ROLE_TEACHER,
    ROLE_STUDENT,
)
from ..acl.models import Role


def check_permission(user, model, action_type, data):

    # allow all users read all models
    if action_type in [PERMISSION_READ, ]:
        return True

    #
    if action_type in [PERMISSION_ADD, ]:
        if model == TeacherSpecialization and data[TeacherSpecialization.teacher_id.key] == user._id:
            return True
        if model == Class and data[Class.teacher_id.key] == user._id:
            return True
        if model == StudentInClass and data[StudentInClass.student_id.key] == user._id:
            return True
    user_roles = list([role.name for role in user.roles])
    if ROLE_TEACHER in user_roles:
        return check_permission_teacher(user, model, action_type, data)

    if ROLE_STUDENT in user_roles:
        return check_permission_student(user, model, action_type, data)


def check_permission_teacher(user, model, action_type, data):

    # teachers can create new specialization
    if action_type in [PERMISSION_ADD, ]:
        if model == Specialization:
            return True

    # only owner can update or delete
    if model == TeacherSpecialization:
        if TeacherSpecialization.where(_id=data['_id'], teacher_id=user._id).count() > 0:
            return True

    # only owner can update or delete
    if model == Class:
        if Class.where(_id=data['_id'], teacher_id=user._id).count() > 0:
            return True


def check_permission_student(user, model, action_type, data):

    # only owner can update or delete
    if model == StudentInClass:
        if StudentInClass.where(_id=data['_id'], student_id=user._id).count() > 0:
            return True

