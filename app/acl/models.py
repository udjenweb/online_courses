# coding: utf-8
from sqlalchemy import (
    Column, String, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship, backref

from ..models import db, db_deny_update
from ..auth.models import User
from sqlalchemy.schema import UniqueConstraint

Base = db.Model


class Resource(Base):
    """ list of resources """
    __tablename__ = 'acl__resources'
    __repr_attrs__ = ['name']

    name = Column(String(32), unique=True, nullable=False, index=True)


@db_deny_update
class Role(Base):
    """ role for users """
    __tablename__ = 'acl__roles'
    __repr_attrs__ = ['name']

    name = Column(String(32), unique=True, nullable=False, index=True)
    # TODO: only lowercase letters and numeric - checking at database


@db_deny_update
class Permission(Base):
    """ permission to role at objects """
    __tablename__ = 'acl__permissions'
    __repr_attrs__ = ['action', 'resource_id', 'role_id']

    resource_id = Column(ForeignKey(Resource._id), nullable=False)
    role_id = Column(ForeignKey(Role._id), nullable=False)
    action = Column(String(32), nullable=False, index=True)

    for_all_objects = Column(Boolean, default=False)  # access for administration of website

    __table_args__ = (UniqueConstraint(*[resource_id, role_id, action],
                                       name='_{}_uc'.format(__tablename__)),)

    resource = relationship(Resource, backref=backref('permissions'), foreign_keys=[resource_id]) # Resource.permissions
    role = relationship(Role, backref=backref('permissions'), foreign_keys=[role_id])             # Role.permissions


@db_deny_update
class UserAssignment(Base):
    """ list of user roles """
    __tablename__ = 'acl__user_assignments'
    __repr_attrs__ = ['user_id', 'role_id']

    user_id = Column(ForeignKey(User._id), nullable=False)
    role_id = Column(ForeignKey(Role._id), nullable=False)

    __table_args__ = (UniqueConstraint(*[user_id, role_id],
                                       name='_{}_uc'.format(__tablename__)),)

    user = relationship(User, backref=backref('assignments'), foreign_keys=[user_id])
    role = relationship(Role, backref=backref('assignments'), foreign_keys=[role_id])

    @staticmethod
    def require_role(required_role_name, foreign_key, error_message, role_error_message=None):
        """
            only if user hav assignment to the role, then cen add new record to depended mode
            depended model must relate tu user model
        :param required_role_name: required role
        :param foreign_key: foreign key name to user model
        :param error_message: error message for exception response
        :param role_error_message: error message if try delete the role
        :return: decorator
        """

        if not role_error_message:
            role_error_message = 'user have field(s) at {depended_model.__tablename__}, need to delete them first.'

        def wrapper(cls):
            depended_model_foreign_key = getattr(cls, foreign_key).key

            # protect to create the record in depended model
            UserAssignment.add_trigger("""\
                CREATE TRIGGER {depended_model.__tablename__}__user_must_be_{required_role_name} 
                    BEFORE INSERT 
                    ON {depended_model.__tablename__} FOR EACH ROW
                BEGIN
                    IF (
                        SELECT COUNT (*) 
                            FROM {Role.__tablename__} roles\
                                LEFT JOIN {UserAssignment.__tablename__} user_assignment
                                    ON roles.{Role._id.key} = user_assignment.{UserAssignment.role_id.key}
                            WHERE roles.{Role.name.key} = '{required_role_name}'
                              AND NEW.{depended_model_foreign_key} = user_assignment.{UserAssignment.user_id.key}   
                        LIMIT 1\
                    ) = 1
                    THEN
                        RETURN NEW;
                    ELSE
                        RAISE EXCEPTION '{error_message}' 
                              USING ERRCODE='P0403';
                    END IF;
                END;\
            """.format(
                        UserAssignment=UserAssignment,
                        depended_model=cls,
                        Role=Role,
                        required_role_name=required_role_name,
                        depended_model_foreign_key=depended_model_foreign_key,
                        error_message=error_message
            ))

            # protect to delete the role if depended model(table) have one or more related records to current user
            cls.add_trigger("""\
                CREATE TRIGGER {UserAssignment.__tablename__}__required__{depended_model.__tablename__} 
                    BEFORE DELETE
                    ON {UserAssignment.__tablename__} FOR EACH ROW
                BEGIN
                    IF (
                            SELECT {Role.name.key} 
                                FROM {Role.__tablename__} roles 
                                WHERE OLD.{UserAssignment.role_id.key} = roles.{Role._id.key}
                                LIMIT 1
                        ) = '{required_role_name}'
                    AND (
                            SELECT COUNT (*)
                                FROM {depended_model.__tablename__} depended_model
                                WHERE OLD.{UserAssignment.user_id.key} = depended_model.{depended_model_foreign_key}
                                LIMIT 1
                        ) = 1
                    THEN \
                        RAISE EXCEPTION '{role_error_message}'
                              USING ERRCODE='P0403';
                    ELSE
                        RETURN OLD;
                    END IF;
                END;\
                """.format(
                UserAssignment=UserAssignment,
                depended_model=cls,
                Role=Role,
                required_role_name=required_role_name,
                depended_model_foreign_key=depended_model_foreign_key,
                role_error_message=role_error_message
            ))

            return cls
        return wrapper


# orm-access: role <-(assignments)-> user
Role.users = relationship(
    User,
    secondary=UserAssignment.__table__,
    backref=backref('roles'),  # User.roles
    foreign_keys=[Role._id, UserAssignment.role_id, User._id, UserAssignment.user_id]
)

