# coding: utf-8
import logging

from flask import Blueprint
from flask import request
from werkzeug.exceptions import BadRequest
from flask import current_app


from tools import (
    response_data_error,
    response_data_success,
)
from config import (
    ROLE_ROOT,
    ROLE_USER,
)


from .models import User
from .user_instance import authorize_user
from .register import register_new_user


log = logging.getLogger(__name__)

mod = Blueprint('auth', __name__)


# authorization by http POST request
@mod.route('/login', methods=['POST', ])
def login():
    # todo: implement authorization by http-headers
    try:
        if not request.json:
            raise KeyError

        data = dict(request.json)
        email = data['email']
        password = data['password']
    except KeyError:
        raise BadRequest('Invalid data format.')

    # check user access keys
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return response_data_error('Invalid email or/and password.', status=401)  # unauthorized

    access_token = authorize_user(user)
    return response_data_success({'access_token': access_token, '_id': user._id})


# register new user
@mod.route('/register', methods=['POST', ])
def register():
    if not request.json:
        raise BadRequest('Invalid data format.')

    data = dict(request.json)

    for require_field in ['email', 'password']:
        if require_field not in data:
            raise BadRequest('You should fill the {field} field'.format(field=require_field))

    email       = data['email']
    password    = data['password']
    firstname   = data['firstname'] if 'firstname' in data else ''
    lastname    = data['lastname']  if 'lastname'  in data else ''

    # todo: add validation of data

    user = register_new_user(email=email, password=password, role=ROLE_USER,
                             firstname=firstname, lastname=lastname).save()

    access_token = authorize_user(user)
    return response_data_success({'access_token': access_token, '_id': user._id})


# todo: add url with return current user profile, for example: 'me / self'

@mod.route('/test', methods=['GET', ])
def my_test():
    print('>>>>>> hello ')
    from .models import User

    print(type(current_app.data))  # <class 'app.models.SqlAlchemyDataLayer'>
    print(type(current_app.data.driver))  # <class 'flask_sqlalchemy.SQLAlchemy'>
    print(type(current_app.data.driver.session))  # <class 'sqlalchemy.orm.scoping.scoped_session'>

    current_app.data.driver.session.add_all([
        User(email='Reluk', password='123')
    ])
    current_app.data.driver.session.commit()

    return response_data_success({'hello': 'world'})

