# coding: utf-8
from sqlalchemy import (
    Column, String, ForeignKey, Integer
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint

from ..auth.models import User
from ..models import db, db_deny_update
from ..acl.models import UserAssignment, Role
from config import ROLE_STUDENT, ROLE_TEACHER

Base = db.Model


class Specialization(Base):
    """ list of resources """
    __tablename__ = 'oc__specialization'
    __repr_attrs__ = ['name']

    name = Column(String(32), unique=True, nullable=False, index=True)


@UserAssignment.require_role(ROLE_TEACHER, 'teacher_id', 'User mast be a teacher for have specialization',
                             role_error_message='Cen not remove assignment: user have specialization(s)')
@db_deny_update
class TeacherSpecialization(Base):
    __tablename__ = 'oc__teacher_specialization'
    __repr_attrs__ = ['specialization_id', 'teacher_id']

    specialization_id = Column(ForeignKey(Specialization._id), nullable=False)
    teacher_id = Column(ForeignKey(User._id), nullable=False)

    __table_args__ = (UniqueConstraint(*[specialization_id, teacher_id],
                                       name='_{}_uc'.format(__tablename__)),)

# orm-access: Specialization <-(TeacherSpecialization)-> user
Specialization.teachers = relationship(
    User,
    secondary=TeacherSpecialization.__table__,
    backref=backref('specializations'),  # User.specializations
    foreign_keys=[Specialization._id, TeacherSpecialization.specialization_id,
                  User._id, TeacherSpecialization.teacher_id]
)


class Class(Base):
    __tablename__ = 'oc__class'
    __repr_attrs__ = ['specialization_id', 'teacher_id']

    specialization_id = Column(ForeignKey(Specialization._id), nullable=False)
    teacher_id = Column(ForeignKey(User._id), nullable=False)

    teacher = relationship(User, backref=backref('teacher_have_classes'), foreign_keys=[teacher_id])


# specialization of class must be eql specialization of teacher
Class.add_trigger("""\
    CREATE TRIGGER {Class.__tablename__}__compare_specialization 
        BEFORE INSERT OR UPDATE
        ON {Class.__tablename__} FOR EACH ROW
    BEGIN
        IF (
            SELECT COUNT (*) 
                FROM {User.__tablename__} users\
                    LEFT JOIN {TeacherSpecialization.__tablename__} user_specialization
                        ON users.{User._id.key} = user_specialization.{TeacherSpecialization.teacher_id.key}
                WHERE NEW.{Class.specialization_id.key} = user_specialization.{TeacherSpecialization.specialization_id.key}
                  AND NEW.{Class.teacher_id.key} = user_specialization.{TeacherSpecialization.teacher_id.key}   
                LIMIT 1\
        ) = 1
        THEN
            RETURN NEW;
        ELSE
            RAISE EXCEPTION 'the teacher have not specialization, required for class' 
                  USING ERRCODE='P0403';
        END IF;
    END;\
    """.format(
    Class=Class,
    User=User,
    TeacherSpecialization=TeacherSpecialization
))


# can not delete teacher specialization if he has one or more classes with this specialization
TeacherSpecialization.add_trigger("""\
    CREATE TRIGGER {TeacherSpecialization.__tablename__}__required__{Class.__tablename__} 
        BEFORE DELETE
        ON {TeacherSpecialization.__tablename__} FOR EACH ROW
    BEGIN
        IF (
            SELECT COUNT (*) 
                FROM {Class.__tablename__} classes\
                WHERE  OLD.{TeacherSpecialization.specialization_id.key} = classes.{Class.specialization_id.key}
                  AND OLD.{TeacherSpecialization.teacher_id.key} = classes.{Class.teacher_id.key}   
                LIMIT 1\
        ) = 0
        THEN
            RETURN NEW;
        ELSE
            RAISE EXCEPTION 'teacher hav class(es) based at current specialization' 
                  USING ERRCODE='P0403';
        END IF;
        
    END;\
    """.format(
    TeacherSpecialization=TeacherSpecialization,
    Class=Class,
    User=User
))


@UserAssignment.require_role(ROLE_STUDENT, 'student_id', error_message='User must be a student for attached to class',
                             role_error_message='Cen not remove assignment: current user is attached to a class(es)')
@db_deny_update
class StudentInClass(Base):
    __tablename__ = 'oc__student_in_class'
    __repr_attrs__ = ['specialization_id', 'teacher_id']

    class_id = Column(ForeignKey(Class._id), nullable=False)
    student_id = Column(ForeignKey(User._id), nullable=False)

    __table_args__ = (UniqueConstraint(*[class_id, student_id],
                                       name='_{}_uc'.format(__tablename__)),)


# orm-access: Class <-(StudentInClass)-> user
Class.students = relationship(
    User,
    secondary=StudentInClass.__table__,
    backref=backref('student_in_classes'),
    foreign_keys=[Class._id, StudentInClass.class_id,
                  User._id, StudentInClass.student_id]
)


