import os


# default config
class BaseConfig(object):
    DEBUG = True
    SECRET_KEY = '12345'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///catalogappwithuserslogin.db'


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///catalogappwithuserslogin.db'


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False