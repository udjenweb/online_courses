# coding: utf-8
import logging
from eve import Eve
from eve_sqlalchemy.validation import ValidatorSQL
from eve_swagger import swagger, add_documentation

from .auth.eve import BasicAuth
from .middlware import allow_cross
import os
from flask import send_from_directory
from config import STATIC_DIR

log = logging.getLogger(__name__)


def create_app(config_name, auth=BasicAuth):
    from config import config
    settings = config[config_name]

    from .models import SqlAlchemyDataLayer
    app = Eve(settings=settings,
              validator=ValidatorSQL, data=SqlAlchemyDataLayer,
              auth=auth,
              static_url_path='/static'
              )

    if config_name == 'debug':
        allow_cross(app)

    # /add views
    from .auth.views import mod as mod_auth
    app.register_blueprint(mod_auth, url_prefix='/auth')

    app.register_blueprint(swagger)

    @app.route('/<path:path>')
    def swagger_ui(path):
        swagger_ui_root_dir = os.path.join(STATIC_DIR, 'swagger')
        return send_from_directory(swagger_ui_root_dir, path)

    return app

