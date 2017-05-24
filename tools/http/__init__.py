# coding: utf-8
from urllib.parse import urlsplit, urlunsplit, urljoin


HTTP_STATUS_UNAUTHORIZED = 401  # для доступа к данному ресурсу требуется авторитизация на сервере
HTTP_STATUS_SUCCESS = 200  #

AUTHORIZATION_HEADER_NAME = 'Authorization'
AUTHORIZATION_HEADER_TYPE_BEARER = 'Bearer'


def split_server_address(address):
    """
    :param address: '0.0.0.0:3000'
    :return: ['0.0.0.0', 3000]
    """
    data = str(address).split(':')
    data = data[0], int(data[1])
    return data


def normalize_url(url, scheme='http'):
    url = '//' + url if len(url.split('//')) == 1 else url
    data = urlsplit(url, scheme=scheme)
    url = urlunsplit(data)
    return url

