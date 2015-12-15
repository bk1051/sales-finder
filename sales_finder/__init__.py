'''
PACKAGE: sales_finder

Authors: Brian Karfunkel (bk1051)
        Taurean Parker (tp823)

This package contains the code to configure and run a Flask web app for
displaying sales data in NYC.

See the README for more information on installation.

We create a Flask app object, as well as a database object to deal with
writing to/reading from the database.

The create_app function is a factory to create and return an app instance.

Much of the structure for the Flask code came from:
Miguel Grinberg. “Flask Web Development.” (O'Reilly) 
'''
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

from data import SalesData

from config import config


# We use the bootstrap plugin for Flask to make pretty web pages
bootstrap = Bootstrap()

# The database is managed by a sqlalchemy object
db = SQLAlchemy()

# Create a sales_data object to manage the data
# Needs to be in the global context so it can be imported, e.g.
# by the manage.py shell command.
sales_data = SalesData()


def create_app(config_name):
    '''Factory to create a Flask web app for SalesFinder'''

    # Initialize the Flask app object
    app = Flask(__name__)

    # config is the dictionary defined in config.py that links
    # a config_name to a subclass of the Config object
    app.config.from_object(config[config_name])

    # Using the config object, call the init_app method to do any
    # configuration-specific initialization
    config[config_name].init_app(app)

    # Since we initialized bootstrap and db without attaching
    # them to an app (i.e. an instance of the Flask object),
    # we need to do that now, using the init_app methods
    bootstrap.init_app(app)
    db.init_app(app)
    # Attach the database to the sales_data object
    sales_data.init_db(db)

    # We import the bluepring here to avoid circular depenedencies
    from .main import main as main_blueprint
    # The blueprint contains the routing information that tells
    # the app how to handle different URL routes. We attach
    # the blueprint to the app here.
    app.register_blueprint(main_blueprint)

    # Now that we have an app object and a config, we can set
    # the limited_data boolean on the sales_data object
    sales_data.limited_data = app.config['LIMITED_DATA']

    # Set testing to use different table
    if app.config['TESTING']:
        sales_data.table = 'sales_test'

    return app




