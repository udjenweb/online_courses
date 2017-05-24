# coding: utf-8
""" integrated tests (is not unit) - not ready yet."""
import requests
from tools import draw
from config import WEB_SERVER_BIND_ADDRESS

SERVER_API_URL = 'http://{host}/api/1.0/'.format(host=WEB_SERVER_BIND_ADDRESS)
# user_keys = {'username': 'root', 'password': 'root'}

response = requests.get(
    url=SERVER_API_URL + 'users?max_results=2&page=3',
)

if response.status_code != 200:
    print('response_data: %s' % str(response.text))
    exit(1)
json = response.json()

print(draw.array(json))
