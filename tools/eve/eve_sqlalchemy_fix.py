# coding: utf-8
from eve_sqlalchemy import SQL
from flask_sqlalchemy import declarative_base


class EveSQLAlchemy(SQL):
    # NOTE: расширение eve_sqlalchemy в классе SQL
    #       использует глобальную переменную db задекларированную в файле db = flask_sqlalchemy.SQLAlchemy()
    #       в классе SQL к ней как self.driver
    #       при инициализации Eve, eve сохраяет у себя ссылку на экземпляр класса SQL(), по адресу app.data
    #       далее ниже в фабрике апп мы подменяем базовую модель
    #       app.data.driver.Model = BaseModel
    #       модифицируя таким образом глобальную переменную 'db' в расширении eve_sqlalchemy
    #       болезненая реакция происходит при тестах, когда не производистся перезагрузка модулей
    #           и при повторном использовании app, расширение eve_sqlalchemy
    #           начинает обращатся к своей глобальной переменной
    #           конкретно к свойству _decl_class_registry -
    #           причем это хитрый класс который ведет свебя как словарь WeakValueDictionary
    #           имеющий параметр data, который после первого прогона приложения наполняется данными
    #       свою базовую модель мы не можем модифицировать так что бы его чистить/обнулять
    #       но есть возможность при инициализации SQL класса из модуля eve_sqlalchemy
    #           обнулять базовую модель,
    #       но по хорошему нужно как то чистить свою базовую модель,
    #           через metaclass(name, bases, class_dict), по образцу как это делается в declarative_base
    # * для информации можно еще посмотреть метод lookup_model у класса SQL
    #       он какраз обращается к _decl_class_registry

    # возможно данную проблему решит декоратор from sqlalchemy.ext.declarative import as_declarative
    # т.к. благодоря нему вызывается declarative_base() каждый раз при создании новой модели
    def init_app(self, app):
        SQL.driver.Model = declarative_base()
        super(EveSQLAlchemy, self).init_app(app)
