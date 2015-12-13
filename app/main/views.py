'''
The main views module, defining the routes for each URL
'''

from flask import render_template, session, redirect, url_for, flash
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from ..data import NoResultsException
from sqlalchemy.exc import SQLAlchemyError
from .. import db, sales_data
from cgi import escape as escape_html

from . import main


def validate_zip_code(form, field):
    '''Validator function for zip code input'''
    zip_code = field.data
    try:
        zip_num = int(zip_code)
    except ValueError:
        # Can't convert to int
        raise ValidationError("ZIP code must be 5 digits")

    if len(zip_code) != 5 or "{:05d}".format(zip_num) != zip_code:
        raise ValidationError("ZIP code must be 5 digits long")


class ZipForm(Form):
    '''Form object to get zip code input from user'''
    zip_code = StringField("Enter ZIP Code", validators=[DataRequired(), validate_zip_code])
    submit = SubmitField("Find Sales")

@main.route('/', methods=['GET', 'POST'])
def index():
    form = ZipForm()
    if form.validate_on_submit():
        # If ZIP code has been posted, save zip to session dictionary
        # and redirect to the results route
        session['zip_code'] = form.zip_code.data
        return redirect(url_for('main.results'))

    return render_template('index.html', form=form)

@main.route('/results/', methods=['GET', 'POST'])
def results():
    form = ZipForm()
    # If valid form results have been POSTed, then display results
    if form.validate_on_submit():
        # Save the POSTed zipcode to the session, then redirect using GET
        # This avoids the "Confirm form resubmission" popup if the
        # user refreshes the page
        session['zip_code'] = form.zip_code.data
        return redirect(url_for('main.results'))

    # Get the graphs
    try:
        results = sales_data.results_for_zip_code(session.get('zip_code'))
        plot = sales_data.plots_for_zip_code(session.get('zip_code'))

    except NoResultsException:
        # If no results, flash a message to user, then redirect to index
        flash("No results from ZIP code %s" % session.get('zip_code'), category='warning')
        return redirect(url_for('main.index'))
    except SQLAlchemyError as e:
        flash("Could not load results for ZIP code %s! Database error: %s" % (
                    session.get('zip_code'), 
                    e
                ), category = 'danger')
        return redirect(url_for('main.index'))
    # If no valid POST results, either because no form data or
    # because we've been redirected using GET after form data was saved
    # to the session, then render the index template
    # Note, use "session.get()" to avoid key error if no form data saved to session
    return render_template('results.html', form=form, zip_code=session.get('zip_code'), results=results, plots=[plot])




@main.route('/zip/<zipcode>/')
def zipcode_results(zip_code):
    try:
        validate_zip_code(zip_code)
        form = ZipForm()
        return render_template('results.html', form=form, zipcode=zip_code)
    except InvalidZipCodeError:
        return render_template('error.html', error_description="Invalid Zip Code")