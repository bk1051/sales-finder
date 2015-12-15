'''
Module to do basic testing for the Flask web app.

Focuses on things in data.py
'''
import unittest
from flask import url_for
from sales_finder import create_app, db, sales_data
import sales_finder.data as data
import manage


class DataTestCase(unittest.TestCase):
    '''Test case for data module'''

    @classmethod
    def setUpClass(cls):
        '''Setup code for the test case'''
        # Create an app instance using the testing configuration
        cls.app = create_app('testing')
        # Initialize the testing database
        manage.init_db(no_confirm=True)


    @classmethod
    def tearDownClass(cls):
        '''Drop testing tables'''
        db.engine.execute("DROP TABLE %s" % sales_data.table)


    def setUp(self):
        '''Setup code for each test'''
        # Creating the app_context means the tests will have
        # access to current_app
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create a test client to test routing etc.
        self.client = self.app.test_client(use_cookies=True)


    def tearDown(self):
        '''Clean up after each test'''
        self.app_context.pop()


    def test_testing_table(self):
        '''Test table name is set correctly for testing environment'''
        self.assertEqual('sales_test', sales_data.table)

    def test_results_for_zip_code(self):
        '''Test that results for zip code are correct'''
        results = sales_data.results_for_zip_code('10460')
        correct = [{'summary_stats': {'Total Number of Sales': '95', 'Median Price Per Sq. Foot': '$157', 'Median Price': '$460,000', 'Median Price Per Residential Unit': '$150,000'}, 
                    'name': 'ZIP Code 10460'},
                   {'summary_stats': {'Total Number of Sales': '2,794', 'Median Price Per Sq. Foot': '$180', 'Median Price': '$415,000', 'Median Price Per Residential Unit': '$197,500'}, 
                    'name': 'The Bronx'},
                   {'summary_stats': {'Total Number of Sales': '221', 'Median Price Per Sq. Foot': '$162', 'Median Price': '$117,000', 'Median Price Per Residential Unit': '$111,333'}, 
                    'name': u'Parkchester              '},
                   {'summary_stats': {'Total Number of Sales': '2,794', 'Median Price Per Sq. Foot': '$180', 'Median Price': '$415,000', 'Median Price Per Residential Unit': '$197,500'}, 
                    'name': 'New York City'}]
        self.assertEqual(results, correct)

    def test_no_results_raises(self):
        '''No results should raise NoResultsException'''
        with self.assertRaises(data.NoResultsException):
            sales_data.results_for_zip_code('00000')

    def test_results_redirect(self):
        '''Test that POSTing to results redirects correctly'''
        response = self.client.post(url_for('main.results'),
                                    data={'zip_code':'10460'}, follow_redirects=False)

        # Assert redirect (code 302)
        self.assertEqual(302, response.status_code)

        # Make sure it's redirecting to "results" not to the index page,
        # as it would if there were an error
        self.assertTrue('results' in response.headers['Location'])

        # And make sure the session object was set correctly
        with self.client.session_transaction() as session:
            self.assertEqual(session['zip_code'], '10460')

    def test_gets_results(self):
        '''Client can GET results when session is set'''
        with self.client.session_transaction() as session:
            session['zip_code'] = '10460'

        get_response = self.client.get(url_for('main.results'), follow_redirects=True)
        self.assertEqual(200, get_response.status_code)


