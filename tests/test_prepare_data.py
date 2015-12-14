from prepare_data import *
import os
import numpy as np
import pandas.util.testing 
from pandas.util.testing import assert_frame_equal
import unittest

class tests(unittest.TestCase):
    
    def test_query_by_zipcode(self):
        df=pd.DataFrame([10001,10003],columns=['zip_code'])
        assert_frame_equal(query_by_zipcode(df,10001),df[df.zip_code == 10001])
        
    def test_strip_whitespace(self):
        str_extra_ws='Hello  There'
        result= 'Hello There'
        self.assertEqual(strip_whitespace(str_extra_ws),result)
    
    def test_create_borough_column(self):
        borough_names=['MANHATTAN','BRONX','BROOKLYN','QUEENS','STATEN ISLAND']
        borough_numbers=[1,2,3,4,5]
        self.assertEqual=(create_borough_column(borough_numbers),borough_names)
        
    def test_rename_columns(self):
        df = pd.DataFrame({'FOO BAR' : np.array([1,2]),'foo-bar' : np.array([1,2])})
        df_result = pd.DataFrame({'foo_bar' : np.array([1,2]),'foobar' : np.array([1,2])})
        assert_frame_equal=(rename_columns(df),df_result)
        
 
        
      
        
        
        
    
        
    
        
               
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    

 
    
    
    
    