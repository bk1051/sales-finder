from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
import os
#from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
#engine = create_engine('postgresql://localhost/sales_finder_dev')

# Initialize app
app = Flask(__name__)
# Use os environmental variable to determine app settings 
# (production, devel, etc.)
app.config.from_object(os.environ['APP_SETTINGS'])
#engine = create_engine(SQLALCHEMY_DATABASE_URL)
#db = SQLAlchemy(app)

# Initialize the flask-bootstrap extension.
# This will allow us to easily use Bootstrap templates in our templates.
bootstrap = Bootstrap(app)


class InvalidZipCodeError(Exception):
    pass


def init_db():
    pass

def connect_db():
    return engine.connect()

@app.route('/')
def index():
    return render_template('index.html')

def validate_zipcode(zipcode):
    if "{:05d}".format(int(zipcode)) != zipcode:
        raise InvalidZipCodeError()
    if len(zipcode) != 5:
        raise InvalidZipCodeError()


@app.route('/zip/<zipcode>/')
def zipcode_results(zipcode):
    try:
        validate_zipcode(zipcode)
        return render_template('results.html', zipcode=zipcode)
    except InvalidZipCodeError:
        return render_template('error.html', error_description="Invalid Zip Code")

@app.route('/<name>')
def hello_name(name):
    return "Hello, %s" % name

if __name__ == '__main__':
    app.run(debug=True)