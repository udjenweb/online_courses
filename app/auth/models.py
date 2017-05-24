# coding: utf-8
import hashlib
from sqlalchemy import (
    Column, String, Integer, DateTime,
)
from sqlalchemy.orm import validates
from flask import current_app

from config import USER_TABLE_NAME
from ..models import db

Base = db.Model


class User(Base):
    __tablename__ = USER_TABLE_NAME
    __repr_attrs__ = ['email', 'role']

    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    firstname = Column(String(255), nullable=True, default='')
    lastname = Column(String(255), nullable=True, default='')

    @staticmethod
    def encrypt(password):
        secret = current_app.config['SECRET_KEY']
        return str(hashlib.sha1(str(password + str(secret)).encode('utf-8')).hexdigest())

    @validates('password')
    def _set_password(self, key, value):
        return self.encrypt(value)

    def check_password(self, password):
        if not self.password:
            return False
        return self.encrypt(password) == self.password


