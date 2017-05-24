# coding: utf-8
from sqlparse.tokens import Token
from .draw import color as _c, array as _v


class ZColorFilter(object):
    def process(self, stream):
        for ttype, value in stream:
            if ttype in Token.Keyword:
                value = _c(value, 'BLUE')
            elif ttype in Token.Name:
                value = _c(value, 'RED')
            else:
                # todo: fix indent-formatter
                value = _c(value, 'RESET')
                pass

            yield ttype, value


def sqlparse_format(sql, encoding=None, **options):
    from sqlparse import engine, formatter, filters, lexer
    options = formatter.validate_options(options)
    stack = engine.FilterStack()
    stack = formatter.build_filter_stack(stack, options)
    stack.postprocess.append(filters.SerializerUnicode())

    stack.preprocess.append(ZColorFilter())
    parsed = stack.run(sql, encoding)
    result = ''.join(parsed)
    return result


def fsql(sql_statement, reindent=True, prefix='#\t', keyword_case='upper', indent_tabs=False,  **kwargs):
    clear_statement = str(sql_statement).replace(':', '')
    f_sql_statement = sqlparse_format(clear_statement,
                                      reindent=reindent,
                                      keyword_case=keyword_case,
                                      indent_tabs=indent_tabs,
                                      **kwargs)
    result = ''.join(["\n" + prefix + line for line in str(f_sql_statement).split('\n')])
    return result + '\n'

