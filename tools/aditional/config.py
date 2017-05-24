# coding: utf-8


# for keeping settings as class
class Config(dict):
    def __init__(self, *args, **kwargs):
        super(Config, self).__init__(*args, **kwargs)
        for key in dir(self):
            if key.isupper():  # only parameters from UPPER LETTERS
                self[key] = getattr(self, key)

