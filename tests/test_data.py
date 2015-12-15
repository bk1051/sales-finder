'''
Module to do basic testing for the Flask web app.
'''
import unittest
from flask import current_app, url_for
from app import create_app, db, sales_data
import app.data as data
#from app.main import views
import manage
import pprint


class DataTestCase(unittest.TestCase):
	@classmethod
	def setUpClass(cls):

		# Create an app instance using the testing configuration
		cls.app = create_app('testing')

		manage.init_db(no_confirm=True)


	@classmethod
	def tearDownClass(cls):
		db.engine.execute("DROP TABLE %s" % sales_data.table)


	def setUp(self):
		# Creating the app_context means the tests will have
		# access to current_app
		self.app_context = self.app.app_context()
		self.app_context.push()

		#db.create_all()
		self.client = self.app.test_client(use_cookies=True)


	def tearDown(self):
		#db.session.remove()
		#db.drop_all()
		#manage.drop_table()
		self.app_context.pop()


	def test_testing_table(self):
		self.assertEqual('sales_test', sales_data.table)

	def test_results_for_zip_code(self):
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
		with self.assertRaises(data.NoResultsException):
			sales_data.results_for_zip_code('00000')
		
	def test_results_redirect(self):
		'''Test that POSTing to results redirects correctly'''
		response = self.client.post(url_for('main.results'), data={'zip_code':'10460'}, follow_redirects=False)
		# Assert redirect (code 302)
		self.assertEqual(302, response.status_code)
		# Make sure it's redirecting to "results" not to the index page, as it would if there were an error
		self.assertTrue('results' in response.headers['Location'])
		# And make sure the session object was set correctly
		with self.client.session_transaction() as session:
			self.assertEqual(session['zip_code'], '10460')

	def test_gets_results(self):
		with self.client.session_transaction() as session:
			session['zip_code'] = '10460'
		# response = self.client.post(url_for('main.results'), data={'zip_code':'10460'}, follow_redirects=True)
		# pprint.pprint(response.headers)
		# pprint.pprint(response.get_data(as_text=True))
		# self.assertEqual(200, response.status_code)
		#self.assertEqual(200, response.status_code)
		get_response = self.client.get(url_for('main.results'), follow_redirects=True)
		self.assertEqual(200, get_response.status_code)
		

