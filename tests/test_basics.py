'''
Module to do basic testing for the Flask web app.
'''
import unittest
from flask import current_app
from app import create_app
#import pprint

class BasicTestCase(unittest.TestCase):

	def setUp(self):
		# Create an app instance using the testing configuration
		self.app = create_app('testing')

		# Creating the app_context means the tests will have
		# access to current_app
		self.app_context = self.app.app_context()
		self.app_context.push()



	def tearDown(self):
		#db.session.remove()
		#db.drop_all()
		#manage.drop_table()
		self.app_context.pop()

	def test_app_exists(self):
		self.assertFalse(current_app is None)

	def test_app_is_testing(self):
		self.assertTrue(current_app.config['TESTING'])
