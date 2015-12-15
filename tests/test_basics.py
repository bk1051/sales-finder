'''
Module to do basic testing for the Flask web app.
'''
import unittest
from flask import current_app
from sales_finder import create_app

class BasicTestCase(unittest.TestCase):
    '''Test case for basic functions'''

    def setUp(self):
        '''Set up before each test'''
        # Create an app instance using the testing configuration
        self.app = create_app('testing')

        # Creating the app_context means the tests will have
        # access to current_app
        self.app_context = self.app.app_context()
        self.app_context.push()



    def tearDown(self):
        '''Clean up after test'''
        self.app_context.pop()

    def test_app_exists(self):
        '''Test that app exists'''
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        '''Test that config TESTING variable is set correctly'''
        self.assertTrue(current_app.config['TESTING'])
