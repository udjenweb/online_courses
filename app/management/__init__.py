# coding: utf-8
from flask_script import Manager

from .install import InstallCommand


def create_manager():
    manager = Manager(usage='app')

    manager.add_command('install', InstallCommand)

    return manager

