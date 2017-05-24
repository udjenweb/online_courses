# coding: utf-8
""" integrated tests (is not unit) - not ready yet."""
import requests
from urllib.parse import urlsplit, urlunsplit, urljoin
from tools.aditional.console import  draw
from config import WEB_SERVER_BIND_ADDRESS
import random
from config import ROLE_STUDENT, ROLE_TEACHER
from json import dumps as json_dumps



SERVER_URL = 'http://{host}/'.format(host=WEB_SERVER_BIND_ADDRESS)
SERVER_API_URL = '{server}/api/1.0/'.format(server=SERVER_URL)

ERROR = 'ERR'
OK = 'OK'
_is_error = lambda data: data['_status'] == ERROR
_is_ok = lambda data: data['_status'] == OK

_items = lambda data: data['_items']


def cp_elm(src, dst, name):
    dst[name] = src[name]
    return dst

_note = lambda text, color=draw.RED: '\n[{}]'.format(draw.color(text, color))


def j(http_response):
    print(_note(http_response.status_code))
    if int(http_response.status_code/10) != 20:
        print('response_data: %s' % str(http_response.text))

    json = dict(http_response.json())

    if http_response.status_code < 300:
        json['_status'] = OK
    print(draw.array(json))

    return json


def make_headers(access_token_root, etag=None):
    headers = {'Authorization': 'Bearer {key}'.format(key=access_token_root)}
    if etag:
        headers['If-Match'] = etag
    return headers


def login(**kwargs):
    resp = j(requests.post(url=urljoin(SERVER_URL, '/auth/login'), json=kwargs))
    if _is_error(resp):
        exit(101)
    return resp['access_token']


def create_or_select(url, headers, json, filters):
    resp = j(requests.get(url=str(url + '?where={}'.format(json_dumps(filters))), headers=headers))
    if len(_items(resp)) > 0:
        resp = _items(resp)[0]
        resp['_status'] = OK
        return resp

    resp = j(requests.post(url=url, headers=headers, json=json))
    if _is_error(resp):
        exit(102)

    return resp



#
print(draw.header('login as root'))
# login as root
access_token_root = login(**{'email': 'root', 'password': 'root'})


#################################################################


#
print(draw.header('create user jen'))
teacher_jen = {'email': 'jen', 'password': '123', 'firstname': 'Evgheni', 'lastname': 'Amanov'}
response = create_or_select(
    url=urljoin(SERVER_API_URL, 'users'),
    headers=make_headers(access_token_root),
    json=teacher_jen,
    filters=cp_elm(teacher_jen, {}, 'email')
)
cp_elm(response, teacher_jen, '_id')
cp_elm(response, teacher_jen, '_etag')



#
print(draw.header('set user jen as teacher'))

response = j(requests.get(
    url=str(urljoin(SERVER_API_URL, 'acl__roles') + '?where={"name": "%s"}' % ROLE_TEACHER),
    headers=make_headers(access_token_root),
))
if _is_error(response):
    exit(103)
ROLE_TEACHER_ID = _items(response)[0]['_id']


j(requests.post(
    url=urljoin(SERVER_API_URL, 'acl__user_assignments'),
    headers=make_headers(access_token_root),
    json={'user_id': teacher_jen['_id'], 'role_id': ROLE_TEACHER_ID}
))


###################################################################


access_token_jen = login(**teacher_jen)

#
print(draw.header('create specialization'))
response = create_or_select(
    url=urljoin(SERVER_API_URL, 'oc__specialization'),
    headers=make_headers(access_token_jen),
    json={'name': 'english'},
    filters={'name': 'english'}
)
english_specialization_id = response['_id']


#
print(draw.header('set specialization for jen'))
j(requests.post(
    url=urljoin(SERVER_API_URL, 'oc__teacher_specialization'),
    headers=make_headers(access_token_jen),
    json={'teacher_id': teacher_jen['_id'], 'specialization_id': english_specialization_id},
))


#
print(draw.header('create new class for jen'))
response = create_or_select(
    url=urljoin(SERVER_API_URL, 'oc__class'),
    headers=make_headers(access_token_jen),
    json={'specialization_id': english_specialization_id, 'teacher_id': teacher_jen['_id']},
    filters={'teacher_id': teacher_jen['_id']}
)
english_class_id = response['_id']



######################################################

#
print(draw.header('create user alex'))
student_alex = {'email': 'alex', 'password': '321', 'firstname': 'Alexandr', 'lastname': 'Lemov'}
response = create_or_select(
    url=urljoin(SERVER_API_URL, 'users'),
    headers=make_headers(access_token_root),
    json=student_alex,
    filters=cp_elm(student_alex, {}, 'email')
)
cp_elm(response, student_alex, '_id')
cp_elm(response, student_alex, '_etag')



#
print(draw.header('set user alex as student'))

response = j(requests.get(
    url=str(urljoin(SERVER_API_URL, 'acl__roles') + '?where={"name": "%s"}' % ROLE_STUDENT),
    headers=make_headers(access_token_root),
))
if _is_error(response):
    exit(103)
ROLE_STUDENT_ID = _items(response)[0]['_id']

j(requests.post(
    url=urljoin(SERVER_API_URL, 'acl__user_assignments'),
    headers=make_headers(access_token_root),
    json={'user_id': student_alex['_id'], 'role_id': ROLE_STUDENT_ID}
))


access_token_alex = login(**student_alex)


######################################################


#
print(draw.header('add alex to class'))
j(requests.post(
    url=urljoin(SERVER_API_URL, 'oc__student_in_class'),
    headers=make_headers(access_token_alex),
    json={'student_id': student_alex['_id'], 'class_id': english_class_id},
))
