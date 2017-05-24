# coding: utf-8
import os
import re
from urllib.parse import urlsplit, urlunsplit, urljoin
from tools.aditional.config import Config
from tools.http import split_server_address
from tools.http import (
    HTTP_STATUS_SUCCESS,
    HTTP_STATUS_UNAUTHORIZED,
)

# compatibility one standard for eve and flask
from tools.http.response_standard_json import (
    RESPONSE_STATUS,
    RESPONSE_ERROR,
    RESPONSE_STATUS_ERROR,
    RESPONSE_STATUS_OK,
)
from tools.eve.auth import (
    PERMISSION_ADD,
    PERMISSION_READ,
    PERMISSION_EDIT,
    PERMISSION_DELETE,
    PERMISSION_ALL,
    PERMISSION_REQUESTS
)
# ===========================    CONSTANTS    ===========================
# /environment:
SQLALCHEMY_DATABASE_URI = 'postgresql://{user}:{password}@{host}/{name}'.format(
                          user=     os.environ.get('DATABASE_USER',     'postgres'),
                          password= os.environ.get('DATABASE_PASSWORD', 'postgres'),
                          host=     os.environ.get('DATABASE_HOST',     'localhost'),
                          name=     os.environ.get('DATABASE_NAME',     'online_courses'))

WEB_SERVER_BIND_ADDRESS = os.environ.get('WEB_SERVER_BIND_ADDRESS', '127.0.0.1:5000')
WEB_SERVER_HOST, WEB_SERVER_PORT = split_server_address(WEB_SERVER_BIND_ADDRESS)

LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', None)  # '/var/log/wikinote.log'; '/dev/null'
DEFAULT_CONFIG = os.getenv('DEFAULT_CONFIG', 'debug')


# /static:
SECRET_KEY = 'this-really-needs-to-be-changed'
EVE_API_PREFIX = ['api', '1.0']   # only for eve resource
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# path to migration folder, created automatically (using by Flask-Migrate)
SQLALCHEMY_MIGRATE_REPO = os.path.join(BASE_DIR, 'migrations')

USER_TABLE_NAME = 'users'

ETAG = '_etag'

ROLE_GUEST = 'guest'
ROLE_ROOT = 'root'
ROLE_USER = 'user'

ROLE_TEACHER = 'teacher'
ROLE_STUDENT = 'student'

ALL_ROLES = [
    ROLE_GUEST, ROLE_ROOT, ROLE_USER,
    ROLE_TEACHER, ROLE_STUDENT
]


LOCAL_PROVIDER_NAME = 'LOCAL'

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# =========================    APP CONFIG(S)    =========================
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = 'true'
from app.resources import get_domains
domains = get_domains()


class BaseConfig(Config):
    DEBUG = False
    SECRET_KEY = SECRET_KEY
    DOMAIN = domains
    RESOURCE_METHODS = ['GET', 'POST', 'DELETE']
    ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']
    ALLOWED_ROLES = []

    USER_TABLE_NAME = USER_TABLE_NAME
    # http://python-eve.org/config.html?highlight=_error#global-configuration

    # todo: make AUTH_FIELD changeable
    LAST_UPDATED = '_updated'
    DATE_CREATED = '_created'
    ID_FIELD = '_id'
    ITEM_LOOKUP_FIELD = ID_FIELD
    ERROR = RESPONSE_ERROR
    ISSUES = '_issues'
    STATUS = RESPONSE_STATUS
    STATUS_OK = RESPONSE_STATUS_OK
    STATUS_ERR = RESPONSE_STATUS_ERROR
    ITEMS = '_items'
    META = '_meta'
    INFO = '_info'
    LINKS = '_links'
    ETAG = ETAG
    VERSIONS = '_versions'  # When VERSIONING is enabled
    VERSION = '_version'
    LATEST_VERSION = '_latest_version'
    VERSION_ID_SUFFIX = '_document'

    PAGINATION = True
    PAGINATION_LIMIT = 50
    PAGINATION_DEFAULT = 25
    QUERY_MAX_RESULTS = 'max_results'

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # False - turn off the Flask-SQLAlchemy event system
    SQLALCHEMY_MIGRATE_REPO = SQLALCHEMY_MIGRATE_REPO
    # SQLALCHEMY_ECHO = True

    URL_PREFIX, API_VERSION = EVE_API_PREFIX

    CACHE_TYPE = 'simple'

    SWAGGER_INFO = {
        'title': 'My Supercool API',
        'version': '1.0',
        'description': 'an API description',
        'termsOfService': 'my terms of service',
        'contact': {
            'name': 'nicola',
            'url': 'http://nicolaiarocci.com'
        },
        'license': {
            'name': 'BSD',
            'url': 'https://github.com/pyeve/eve-swagger/blob/master/LICENSE',
        }

    }
    SWAGGER_HOST = WEB_SERVER_BIND_ADDRESS


class DebugConfig(BaseConfig):
    DEBUG = True


config = {
    'base':    BaseConfig(),
    'debug':   DebugConfig(),
    'testing': DebugConfig(),
}
config['default'] = config['debug']


# ==============================    END    =============================

