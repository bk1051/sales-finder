import pandas as pd
import numpy as np
import requests
import os

def download_data(rootdir):
	urls = [
		"http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
		"http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
		"http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
		"http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
		"http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
	]
	for url in urls:
		download(url, rootdir)

def download(url, rootdir, overwrite=False):
	local_filename = rootdir + url.split('/')[-1]
	if not overwrite and os.path.exists(local_filename):
		print "Skipping %s (already exists)" % local_filename
		return local_filename

	print "Dowloading %s to %s" % (url, local_filename)
	r = requests.get(url, stream=True)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				f.write(chunk)
	return local_filename

def stack_data(directory):
	frames = []
	for infile in os.listdir(directory):
		_, ext = os.path.splitext(infile)
		if os.path.isfile(os.path.join(directory, infile)) and \
			ext.upper() in (".XLS", ".XLSX"):
			frames.append(load_sales_file(os.path.join(directory, infile)))
		else:
			print "Skipping %s" % infile
	return pd.concat(frames)

def field_cleaner(fieldname):
	newname = fieldname.lower()
	newname = newname.replace(" ", "_")
	newname = newname.replace("-", "")
	return newname


def rename_columns(dataframe):
	dataframe.columns = [field_cleaner(field) for field in dataframe.columns]

def load_cleaned_data():
	dataroot = "data/"
	download_data(dataroot)
	raw = stack_data(dataroot)
	rename_columns(raw)

	data = get_clean_data(raw)
	return data

def get_clean_data(raw_data):
	# Restrict to data with non-trivial sale prices
	# Return a copy of subset raw_data, to avoid SettingWithCopyWarning
	clean = raw_data[raw_data.sale_price >= 100].copy()
	clean['log_sale_price'] = np.log(clean.sale_price)
	clean['sale_price_per_sqft'] = clean.sale_price / clean.gross_square_feet
	clean.loc[clean.gross_square_feet==0, 'sale_price_per_sqft'] = np.nan
	clean['sale_price_per_res_unit'] = clean.sale_price / clean.residential_units


	return clean

'''
Years= range(2003,2015)
sales_data = pd.DataFrame()
for year in Years:
	path='~/Desktop/SalesFinder/Data/year_%d.csv' % year
	df= pd.read_csv(path)
	df['year'] = year
    	sales_data = sales_data.append(df, ignore_index=True)
'''

def load_sales_file(filename):
	'''Load the sales file, skipping header rows'''
	return pd.read_excel(filename, skiprows=[0,1,2,3])
