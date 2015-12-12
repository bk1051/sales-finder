from flask import Flask, render_template, session, url_for, redirect
from flask.ext.bootstrap import Bootstrap
import os

from flask.ext.wtf import Form
from wtforms import StringField, SubmitField

from flask.ext.script import Manager

# from config import config

from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy import create_engine
#engine = create_engine('postgresql://localhost/sales_finder_dev')

from sqlalchemy.exc import ProgrammingError
import psycopg2


# Initialize app
app = Flask(__name__)
# Use os environmental variable to determine app settings 
# (production, devel, etc.)
app.config.from_object(os.environ['APP_SETTINGS'])
#engine = create_engine(SQLALCHEMY_DATABASE_URL)
db = SQLAlchemy(app)

# Initialize the flask-bootstrap extension.
# This will allow us to easily use Bootstrap templates in our templates.
bootstrap = Bootstrap(app)

# Initialize the command-line manager from Flask-Script
manager = Manager(app)


class InvalidZipCodeError(Exception):
    pass

class ZipForm(Form):
    zipcode = StringField("Enter ZIP Code")
    submit = SubmitField("Find Sales")


# class Sale(db.Model):
#     __tablename__ = 'sales'
#     id = db.Column(db.Integer, primary_key = True)
#     sale_price = db.Column(db.Integer)

#     def __repr__(self):
#         return '<Sale %r: %r>' % (self.id, self.sale_price)

def field_cleaner(fieldname):
    newname = fieldname.lower()
    newname = newname.replace(" ", "_")
    newname = newname.replace("-", "")
    return newname


def rename_columns(dataframe):
    dataframe.columns = [field_cleaner(field) for field in dataframe.columns]


def get_zip_code_data(database, zip_code):
    return pd.read_sql_query("select * from _sales_data where zip_code=%s" % zip_code, database.engine)

def init_db(database):
    '''Database doesn't know about the sales_data table, so it doesn't know how to drop it!'''
    #database.drop_all()
    try:
        database.engine.execute("DROP TABLE _sales_data")
    except ProgrammingError:
        print "No existing sales data table"
    except Exception as e:
        print type(e)
        print e

    import pandas as pd
    urls = [
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
    ]
    df = pd.read_excel(urls[0], skiprows=[0,1,2,3])
    print df.head()
    rename_columns(df)
    df.to_sql('_sales_data', database.engine)

# def connect_db():
#     return engine.connect()

@app.route('/', methods=['GET', 'POST'])
def index():
    form = ZipForm()
    # If valid form results have been POSTed, then display results
    if form.validate_on_submit():
        # Save the POSTed zipcode to the session, then redirect using GET
        # This avoids the "Confirm form resubmission" popup if the
        # user refreshes the page
        session['zipcode'] = form.zipcode.data
        return redirect(url_for('index'))

    # If no valid POST results, either because no form data or
    # because we've been redirected using GET after form data was saved
    # to the session, then render the index template
    # Note, use "session.get()" to avoid key error if no form data saved to session
    return render_template('index.html', form=form, zipcode=session.get('zipcode'))


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
    manager.run()