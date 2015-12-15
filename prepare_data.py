import pandas as pd
import numpy as np
#import requests
import re
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

def create_borough_column(borough):
    if borough == 1:
        return 'MANHATTAN'
    if borough == 2:
        return 'BRONX'
    if borough == 3:
        return 'BROOKLYN'
    if borough == 4:
        return 'QUEENS'
    if borough == 5:
        return 'STATEN ISLAND'

def rename_building_categ_column(build_id):
    coops=['09','10']
    condos=['4','15','16','17']
    
    if build_id == '01':
       return 'ONE FAMILY HOMES'
    if build_id == '02':
        return 'TWO FAMILY HOMES'
    if build_id ==  '03':
        return 'THREE FAMILY HOMES'
    if build_id in condos:
        return 'CONDOS'
    if build_id in coops:
        return 'COOPS'


def strip_whitespace(column):
    'Remove Extra Whitespace From Columns Values'
    column=str(column)
    return re.sub( '\s+', ' ', column ).strip()
    

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
    clean = clean[clean.residential_units != 0]

    # Rename Columns
    clean['building_class_category']= clean['building_class_category'].apply(strip_whitespace)
    clean['building_class_id']=clean['building_class_category'].apply(lambda x: x.partition(' ')[0])
    clean['building_type']=clean['building_class_id'].apply(rename_building_categ_column)
    clean['borough_name'] = clean['borough'].apply(create_borough_column)

    #Subset Data
    columns=['borough_name','zip_code','neighborhood','building_type',
             'residential_units','sale_price','log_sale_price',
             'sale_price_per_sqft','sale_price_per_res_unit']
    clean = clean[clean.building_type != None]

   
    clean=clean[columns]
    return clean


def query_by_zipcode(data,zipcode):
    try:
        data=data[data.zip_code == zipcode]
        if data.empty:
            print 'There Is No Data On Zipcode %s' %zipcode
        else:
            return data
    
    except TypeError:
        print 'Invalid Input. Please Enter A Value In Non-String Format'





def load_sales_file(filename):
    '''Load the sales file, skipping header rows'''
    return pd.read_excel(filename, skiprows=[0,1,2,3])
