# coding: utf-8
import sqlparse
import re
from sqlalchemy import Table, event, DDL


def extract_identifier(idf):
    assert isinstance(idf, sqlparse.sql.Identifier)
    assert idf[0].ttype == sqlparse.tokens.Name
    return idf[0].normalized


def get_identifier_value(identifier):
    if isinstance(identifier, sqlparse.sql.Identifier):
        yield extract_identifier(identifier)

    if isinstance(identifier, sqlparse.sql.IdentifierList):
        for item in identifier.get_identifiers():
            if isinstance(item, sqlparse.sql.IdentifierList):
                yield get_identifier_value(item)
            else:
                yield extract_identifier(item)


class Trigger(list):
    def __init__(self, seq=(), source=None, name=None, tables=None, procedure=None, trigger=None):
        super(Trigger, self).__init__(seq)
        self.source = source
        self.name = name
        self.tables = tables

        self.procedure = procedure
        self.trigger = trigger


def postgres_sql_trigger_convert(sql_statement, procedure_prefix='_procedure'):
    # to parse sql statement
    parsed = sqlparse.parse(sql_statement)[0]  # <class 'sqlparse.sql.Statement'>

    trigger_items = []
    trigger_name = None
    procedure_body = None

    tables_name_list = None

    # to parse trigger name, bod and procedure body
    for number, item in enumerate(parsed):

        # extract trigger name
        if item.match(sqlparse.tokens.Keyword, 'TRIGGER'):
            if trigger_name:
                raise KeyError('duplicate of TRIGGER.')
            trigger_name = extract_identifier(parsed[number + 2])  # ignore space

        # extract table name
        if item.match(sqlparse.tokens.Keyword, 'ON'):
            if tables_name_list:
                raise KeyError('duplicate of table_name.')
            tables_name_list = get_identifier_value(parsed[number + 2])

        #
        if trigger_name and isinstance(item, sqlparse.sql.Begin):
            # get procedure body
            if procedure_body:
                raise KeyError('invalid format of TRIGGER.')
            procedure_body = item
        else:
            # create trigger body
            trigger_items.append(item)

    # cen not fined trigger name or procedure body
    if not trigger_name or not procedure_body:
        raise KeyError('name trigger or function body is not parsed')

    # validate procedure body: at end statement must be ';'
    last_token = procedure_body[-1]
    if not last_token.match(sqlparse.tokens.Punctuation, ';'):
        procedure_body.insert_after(last_token, sqlparse.sql.Token(sqlparse.tokens.Punctuation, ';'))

    # validate trigger: remove at end ';'
    for i, elm in reversed(list(enumerate(trigger_items))):
        if elm.match(sqlparse.tokens.Punctuation, ';'):
            trigger_items.pop(i)
        elif elm.ttype == sqlparse.tokens.Whitespace:
            trigger_items.pop(i)
        else:
            break

    # generate procedure name
    procedure_name = trigger_name + procedure_prefix

    # create procedure
    procedure_statement = re.sub(r'\s+', ' ', """\
        CREATE OR REPLACE FUNCTION {f_name}() RETURNS trigger AS ${f_name}$
            {body}
        ${f_name}$ LANGUAGE plpgsql;\
        """.format(f_name=procedure_name, body=procedure_body))

    # create trigger
    trigger_statement = re.sub(r'\s+', ' ', """\
        {trigger} 
            EXECUTE PROCEDURE
            {f_name}();
        """.format(trigger=sqlparse.sql.Statement(trigger_items), f_name=procedure_name))
    return Trigger([procedure_statement, trigger_statement],
                   source=sql_statement,
                   name=trigger_name,
                   procedure=procedure_statement,
                   trigger=trigger_statement,
                   tables=list(tables_name_list)
                   )


def register_db_event(model, event_name, dll, *args, **kw):
    table_name = model if isinstance(model, str) else model.__tablename__

    def listener(table, bind, **kwargs):
        if table.name == table_name:
            dll(table, bind, **kwargs)

    return event.listen(Table, event_name, listener, *args, **kw)


def add_trigger(sql_statement):
    trigger = postgres_sql_trigger_convert(sql_statement)
    assert len(trigger.tables) == 1
    register_db_event(trigger.tables[0], 'before_create', DDL(trigger.procedure))
    register_db_event(trigger.tables[0], 'after_create',  DDL(trigger.trigger))
    return trigger
