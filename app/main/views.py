'''
The main views module, defining the routes for each URL
'''

from flask import render_template


from . import main

@main.route('/')
def index():
	return "Hello World"