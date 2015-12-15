'''
Configuration module

This module defines several configuration objects (classes).

Each environment can use a different object to set app-wide variables. The config objects are
attached to a Flask app instance by calling config.from_object().

The base class, Config, defines a static init_app() method, which can be used to do any setup
at configuration time.
'''
import os

class Config(object):
    '''Base class for config objects.'''
    DEBUG = False
    TESTING = False
    WTF_CSRF_ENABLED = True # cross-site request forgery protection for forms
                            # set to false when testing, since not using a real server will cause
                            # problems
    CSRF_ENABLED = True

    SECRET_KEY = 'this-really-needs-to-be-changed'

    basedir = os.path.abspath(os.path.dirname(__file__))
    #SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL'] or \
    SQLALCHEMY_DATABASE_URI =                           'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    SQLALCHEMY_TRACK_MODIFICATIONS = False # to squelch the warning; tracking modifications is
                                           # resource intensive

    # Flag for whether to use all data or just a subset
    LIMITED_DATA = False

    @staticmethod
    def init_app(app):
        '''Code to run at configuration time.
        (Empty for now, but can be overridden in subclasses)'''
        pass


class ProductionConfig(Config):
    '''Production environment'''
    DEBUG = False


class StagingConfig(Config):
    '''Staging environment for Heroku'''
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    '''Development environment'''
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    '''Testing environment'''
    TESTING = True
    LIMITED_DATA = True

    WTF_CSRF_ENABLED = False


# The config dictionary relates an environment name to the right class
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}
