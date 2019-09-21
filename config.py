import os
class Config(object):
    MONGO_URI = os.environ.get('MONGO_URI')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    