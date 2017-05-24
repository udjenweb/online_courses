# coding: utf-8
from colorama import Fore, Back, Style
import json
import re
from ...json.serializer import json_serial


# more colors
# https://github.com/jkbrzt/httpie/blob/497a91711af7c97dcb70fe113a11cd90a7e070fd/httpie/output/formatters/colors.py


BLUE    = Fore.BLUE
BLACK   = Fore.BLACK
MAGENTA = Fore.MAGENTA
RED     = Fore.RED
YELLOW  = Fore.YELLOW
GREEN   = Fore.GREEN
CYAN    = Fore.CYAN
WHITE   = Fore.WHITE

DEFAULT_COLOR = Fore.RESET

STYLE_BRIGHT = Style.BRIGHT
STYLE_BRIGHT = Style.DIM
STYLE_NORMAL = Style.NORMAL
DEFAULT_STYLE = Style.RESET_ALL


def in_color(message, color, default_color=DEFAULT_COLOR):
    return '{color}{message}{default_color}'.format(color=color, message=message, default_color=default_color)


def color(message, color=WHITE):
    color = getattr(Fore, str(color).upper(), color)
    return in_color(message, color)


def header(text, str_len=74, color=BLUE, default_color=DEFAULT_COLOR):
    color = getattr(Fore, str(color).upper(), color)
    text = ' %s ' % text
    indent = (str_len - len(text))/2
    while indent > 0:
        indent -= 1
        text = '-%s-' % text
    if len(text) < str_len:
        text += '-'
    return '\n{color}{text}{default_color}'.format(color=color, text=text, default_color=default_color)


def _parse_end_string(value):
    end = ''
    if value[-2:] == ', ':
        value, end = value[:-2], value[-2:]
    elif value[-1:] in ['[', '{']:
        value, end = "", value
    return value, end


def _get_value_type(value):
    if len(value) < 1:
        raise KeyError

    if value[0] == '"':
        return str
    elif value[0] in ".0123456789":
        return int
    elif value in ['true', 'false', 'null']:
        return bool
    else:
        raise KeyError


def _parse_dict_line(line, color_key=YELLOW, color_str=MAGENTA, color_int=RED, color_bool=BLUE,
                     default_color=DEFAULT_COLOR):
    mask_dict = re.compile(r'''
                           ^
                           (?P<indent>[ ]*)
                           (?P<key>"\w*")
                           (?P<separator>[:][ ])
                           (?P<value>[^\n]*)
                           ''', flags=re.MULTILINE | re.VERBOSE)
    result = mask_dict.findall(line)
    if len(result) != 1:
        raise KeyError

    indent, key, separator, value = result[0]
    value, end = _parse_end_string(value)

    color_value = default_color
    try:
        value_type = _get_value_type(value)
    except KeyError:
        value_type = None
    if value_type == str: color_value = color_str
    if value_type == int: color_value = color_int
    if value_type == bool: color_value = color_bool

    result = "{indent}{color_key}{key}{color_reset}{separator}{color_value}{value}{color_reset}{end}" \
             "".format(indent=indent, key=key, separator=separator, value=value, end=end,
                       color_key=color_key, color_value=color_value,
                       color_reset=default_color,
                       )
    return result


def _parse_list_line(line, color_key=YELLOW, color_str=MAGENTA, color_int=RED, color_bool=BLUE,
                     default_color=DEFAULT_COLOR):
    mask_list = re.compile(r'''
                           ^
                           (?P<indent>[ ]*)
                           (?P<value>[^\n]*)
                           ''', flags=re.MULTILINE | re.VERBOSE)
    result = mask_list.findall(line)
    if len(result) != 1:
        raise KeyError

    indent, value = result[0]
    value, end = _parse_end_string(value)

    color_value = default_color
    try:
        value_type = _get_value_type(value)
    except KeyError:
        raise
    if value_type == str: color_value = color_str
    if value_type == int: color_value = color_int
    if value_type == bool: color_value = color_bool

    result = "{indent}{color_value}{value}{color_reset}{end}" \
             "".format(indent=indent, value=value, end=end,
                       color_value=color_value,
                       color_reset=default_color,
                       )
    return result


def array(data, *, color_key=YELLOW, color_str=MAGENTA, color_int=RED, color_bool=BLUE, default_color=DEFAULT_COLOR,
       inline=False, indent=4):
    color_set = dict(color_key=color_key, color_str=color_str, color_int=color_int, color_bool=color_bool,
                     default_color=default_color)
    # color_set = dict(color_key='<YELLOW>', color_str='<MAGENTA>', color_int='<RED>', color_bool='<BLUE>',
    #                  default_color='<DEFAULT>')
    # may be better to return object who lets customize, example: _v(dict).inline()
    if inline:
        indent = 0
    separators = (', ', ': ')
    dump = json.dumps(
        data,
        indent=indent,
        sort_keys=True,
        separators=separators,
        default=json_serial,
        )
    # parse JSON
    result = ''
    for line in dump.split('\n'):
        if not inline:
            result += '\n' if result != '' else ''

        try:
            result += _parse_dict_line(line, **color_set)
            continue
        except KeyError:
            pass

        try:
            result += _parse_list_line(line, **color_set)
            continue
        except KeyError:
            pass

        if len(re.findall(r"[\[\]{}]", line)) == 1:
            result += line
            continue
        raise KeyError
    return result

