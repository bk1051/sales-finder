'''These functions handle HTTP error responses, displaying the correct html template'''
from flask import render_template
from . import main

@main.app_errorhandler(404)
def page_not_found(error):
    '''Handle 404 errors'''
    print "Error %s" % error
    return render_template('error.html', 
        error_description="We couldn't find the page you were looking for - oh! for!"), 404

@main.app_errorhandler(500)
def internal_server_error(error):
    '''Handle 500 errors'''
    print "Error %s" % error
    return render_template('error.html', 
        error_description="Uh, our bad! Our server errored internally"), 500