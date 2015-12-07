
'''

Need script to init the database
- Download data if necessary
- Load into dataframes
- do cleaning
- output to sql database
-- upgrade if exists?

To install, do pip install the package, then run the init script

Create model from the pd.to_sql output? Or just wing it? or create it explicitly?

Then, query database with given route

Generate results:
- Reload to data frame?
- Create metrics (mean, median, number of sales, std error of the mean)
- Create graphs?
-- If using matplotlib, output to pngs? Then display?
-- Otherwise...port to JS? to_json? Or is the json file the response?
-- if post, do query, get results, return json
'''
