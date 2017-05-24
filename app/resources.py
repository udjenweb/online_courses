# coding: utf-8
from tools import Domains


def get_domains():
    domains = Domains()

    from .auth.models import User
    # todo: remove password and owner fields from resource user data
    domains.add(User, url='users')

    from .acl.models import Resource, Role, Permission, UserAssignment
    domains.add(Resource, disable_documentation=True)
    domains.add(Role)
    domains.add(Permission)
    domains.add(UserAssignment)

    from .online_courses.models import Specialization, TeacherSpecialization, Class, StudentInClass
    domains.add(Specialization)
    domains.add(TeacherSpecialization)
    domains.add(Class)
    domains.add(StudentInClass)

    return domains

