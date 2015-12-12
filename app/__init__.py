'''
PACKAGE: app

This package contains the code to configure and run the Flask web app.
'''
'''

Need script to init the database
- Download data if necessary
- Load into dataframes
- do cleaning
- output to sql database
-- upgrade if exists?

To install, do pip install the package, then run the init script

Create model from the pd.to_sql output? Or just wing it? or create it explicitly?

Then, query database with given route

Generate results:
- Reload to data frame?
- Create metrics (mean, median, number of sales, std error of the mean)
- Create graphs?
-- If using matplotlib, output to pngs? Then display?
-- Otherwise...port to JS? to_json? Or is the json file the response?
-- if post, do query, get results, return json
'''


from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy

from config import config


bootstrap = Bootstrap()
db = SQLAlchemy()

def create_app(config_name):
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

	# We import the bluepring here to avoid circular depenedencies
	from .main import main as main_blueprint
	# The blueprint contains the routing information that tells
	# the app how to handle different URL routes. We attach
	# the blueprint to the app here.
	app.register_blueprint(main_blueprint)

	return app



# import os

# from flask.ext.wtf import Form
# from wtforms import StringField, SubmitField

# from flask.ext.script import Manager

# # from config import config

# #from sqlalchemy import create_engine
# #engine = create_engine('postgresql://localhost/sales_finder_dev')

# from sqlalchemy.exc import ProgrammingError
# import psycopg2



# # Initialize app
# app = Flask(__name__)
# # Use os environmental variable to determine app settings 
# # (production, devel, etc.)
# #engine = create_engine(SQLALCHEMY_DATABASE_URL)
# db = SQLAlchemy(app)

# # Initialize the flask-bootstrap extension.
# # This will allow us to easily use Bootstrap templates in our templates.
# bootstrap = Bootstrap(app)

# # Initialize the command-line manager from Flask-Script
# manager = Manager(app)
