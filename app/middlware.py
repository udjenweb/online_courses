# coding: utf-8
from flask import request, current_app


def allow_cross(app):  # this is dummy for development!

    methods = [ 'GET',      # SELECT
                'POST',     # INSERT
                'PUT',      # replace (all cell of row)
                'PATCH',    # update (may only one cell of row)
                'DELETE',   # remove
    ]
    headers = ['application/json']

    methods = ', '.join(sorted(x.upper() for x in methods))
    headers = ', '.join(x.upper() for x in headers)

    def prepare_headers(response):
        h = response.headers
        h['Access-Control-Allow-Origin'] = request.headers['ORIGIN']  # allow current request domain
        h['Access-Control-Allow-Credentials'] = 'true'  # allow authorization and cookie data
        h['Access-Control-Allow-Methods'] = methods     # allow methods
        h['Access-Control-Allow-Headers'] = headers     # allow headers
        h['Access-Control-Max-Age'] = str(21600)        # say a browser to remember the allows for this period of time
        return response

    @app.before_request
    def before_request():
        if request.method == 'OPTIONS':
            response = current_app.make_default_options_response()
            response = prepare_headers(response)
            response.headers['Access-Control-Allow-Headers'] = 'content-type, authorization, if-match'
            return response

    @app.after_request
    def after_request(response):
        if request.method == 'OPTIONS':
            return response
        if 'ORIGIN' not in request.headers:
            return response
        response = prepare_headers(response)
        return response


