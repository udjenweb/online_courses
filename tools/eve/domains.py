from flask import current_app


class Domains(dict):
    def __init__(self, *args, **kwargs):
        super(Domains, self).__init__(*args, **kwargs)
        self._models = {}

    def get_url(self, model, _id=None):
        config = current_app.config
        url = ''
        if 'BASE_URL_PREFIX' in config and config['BASE_URL_PREFIX']:
            url += '%s' % config['BASE_URL_PREFIX']
        if 'URL_PREFIX' in config and config['URL_PREFIX']:
            url += '/%s' % config['URL_PREFIX']
        if 'API_VERSION' in config and config['API_VERSION']:
            url += '/%s' % config['API_VERSION']
        url += '/%s' % self.get_name(model)
        if _id:
            url += '/%s' % str(_id)
        return url

    def add(self, model, name=None, **kwargs):
        if not name:
            name = model.__tablename__
        self._models[name] = model
        self.update({name: model._eve_schema})
        if kwargs:
            self[name].update(kwargs)
        return self[name]

    def get_name(self, model):
        for k, v in self._models.items():
            if v == model:
                return k
        raise KeyError

    def get_model(self, resource_name):
        return self._models[resource_name]

