# coding: utf-8
import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Command
from flask import current_app
from sqlalchemy import text

from app import create_app


class ApplyTriggersCommand(Command):
    def run(self):
        conn = current_app.data.driver.engine.connect()
        from app.models import db

        for trigger in sorted(db.Model.__triggers__, key=lambda x: x.name, reverse=False):
            # TODO need to remove all triggers fro database - set as additional function
            print('>>> add trigger:', trigger.name)
            conn.execute(text("""DROP TRIGGER IF EXISTS {} ON {} ;""".format(trigger.name, trigger.tables[0] )))
            conn.execute(trigger.procedure)
            conn.execute(trigger.trigger)
        conn.close()


class DropAllTriggersCommand(Command):
    def run(self):
        conn = current_app.data.driver.engine.connect()
        # TODO need to remove all trigger functions
        print('>>> drop all triggers...')

        conn.execute(text('''\
            CREATE OR REPLACE FUNCTION strip_all_triggers() RETURNS text AS $$ DECLARE
                triggNameRecord RECORD;\
                triggTableRecord RECORD;\
            BEGIN\
                FOR triggNameRecord IN select distinct(trigger_name) from information_schema.triggers where trigger_schema = 'public' LOOP
                    FOR triggTableRecord IN SELECT distinct(event_object_table) from information_schema.triggers where trigger_name = triggNameRecord.trigger_name LOOP
                        RAISE NOTICE 'Dropping trigger: % on table: %', triggNameRecord.trigger_name, triggTableRecord.event_object_table;
                        EXECUTE 'DROP TRIGGER ' || triggNameRecord.trigger_name || ' ON ' || triggTableRecord.event_object_table || ';';
                    END LOOP;
                END LOOP;
            
                RETURN 'done';
            END;
            $$ LANGUAGE plpgsql SECURITY DEFINER;
            
            select strip_all_triggers();
        '''))
        conn.close()


def create_manager():
    eve_app = create_app(os.getenv('FLASK_CONFIG') or 'default')

    manager = Manager(eve_app)

    from app.models import db
    # add tools to manager  https://flask-script.readthedocs.io/en/latest/#sub-managers
    MigrateCommand.add_command('push_triggers', ApplyTriggersCommand)
    MigrateCommand.add_command('drop_triggers', DropAllTriggersCommand)
    migrate = Migrate(eve_app, db)
    manager.add_command('db', MigrateCommand)

    from app.management import create_manager as create_app_manager
    manager.add_command('app', create_app_manager())

    return manager


if __name__ == '__main__':
    base_manager = create_manager()
    base_manager.run()

