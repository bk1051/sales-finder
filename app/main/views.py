'''
The main views module, defining the routes for each URL
'''

from flask import render_template, session, redirect, url_for
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, ValidationError
from wtforms.validators import Required

from . import main


def validate_zipcode(form, field):
    '''Validator function for zip code input'''
    zipcode = field.data
    try:
        zip_num = int(zipcode)
    except ValueError:
        # Can't convert to int
        raise ValidationError("ZIP code must be 5 digits")

    if len(zipcode) != 5 or "{:05d}".format(zip_num) != zipcode:
        raise ValidationError("ZIP code must be 5 digits long")


class ZipForm(Form):
    '''Form object to get zip code input from user'''
    zipcode = StringField("Enter ZIP Code", validators=[Required(), validate_zipcode])
    submit = SubmitField("Find Sales")


@main.route('/', methods=['GET', 'POST'])
def index():
    form = ZipForm()
    # If valid form results have been POSTed, then display results
    if form.validate_on_submit():
        # Save the POSTed zipcode to the session, then redirect using GET
        # This avoids the "Confirm form resubmission" popup if the
        # user refreshes the page
        session['zipcode'] = form.zipcode.data
        return redirect(url_for('main.index'))

    # If no valid POST results, either because no form data or
    # because we've been redirected using GET after form data was saved
    # to the session, then render the index template
    # Note, use "session.get()" to avoid key error if no form data saved to session
    return render_template('index.html', form=form, zipcode=session.get('zipcode'))




@main.route('/zip/<zipcode>/')
def zipcode_results(zipcode):
    try:
        validate_zipcode(zipcode)
        return render_template('results.html', zipcode=zipcode)
    except InvalidZipCodeError:
        return render_template('error.html', error_description="Invalid Zip Code")