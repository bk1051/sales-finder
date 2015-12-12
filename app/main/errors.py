from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(error):
	print "Error %s" % error
	return render_template('error.html', error), 404