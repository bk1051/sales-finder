import os

class Config(object):
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    #SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/sales_finder_dev'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flag for whether to use all data or just a subset
    LIMITED_DATA = False

    @staticmethod
    def init_app(app):
        pass

class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/sales_finder_dev'


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    

class TestingConfig(Config):
    TESTING = True
    LIMITED_DATA = True

    WTF_CSRF_ENABLED = False
    #SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/sales_finder_test'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}