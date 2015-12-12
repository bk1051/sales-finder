'''
Module to manipulate and store data
'''
import pandas as pd
import numpy as np
import sys

# Borough mapping dict
BOROUGH_MAPPING = {
    1: "Manhattan",
    2: "The Bronx",
    3: "Brooklyn",
    4: "Queens",
    5: "Staten Island"
}

BUILDING_CLASS_MAPPING = {
    '01': "Single-Family Homes",
    '02': "Two- to Three-Family Homes",
    '03': "Two- to Three-Family Homes",

}

def field_cleaner(fieldname):
    '''Take a field (column name), convert to lowercase, strip out hyphens,
        and replace spaces with underscores. Return result.'''
    newname = fieldname.lower()
    newname = newname.replace(" ", "_")
    newname = newname.replace("-", "")
    return newname


def rename_columns(dataframe):
    '''Clean all the column names in a dataframe'''
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

def building_class_to_type(build_id):
    '''Create property type from building class ID codes'''
    single_family = ['01']
    two_three_family = ['02', '03']
    multifamily_rental = ['07', '08', '11A', '14']
    coops=['09','10', '17']
    condos=['4','12','13','15']

    if build_id in single_family:
        return "Single-Family Homes"
    if build_id in two_three_family:
        return "2- to 3-Family Homes"
    if build_id in multifamily_rental:
        return "4+ Unit Rental Buildings"
    if build_id in coops:
        return "Co-ops"
    if build_id in condos:
        return "Condos"
    return "Other"


def strip_whitespace(value):
    '''Remove whitespace from column values'''
    return str(value).strip()



def clean_data(raw_data):
    '''Clean raw sales data'''
    # First, rename columns
    rename_columns(raw_data)

    # Restrict to data with non-trivial sale prices and residential units
    # Return a copy of subset raw_data, to avoid SettingWithCopyWarning
    clean = raw_data[(raw_data.sale_price >= 100) & (raw_data.residential_units > 0)].copy()

    # Create fields
    clean['log_sale_price'] = np.log(clean.sale_price)

    clean['sale_price_per_sqft'] = clean.sale_price / clean.gross_square_feet
    clean.loc[clean.gross_square_feet==0, 'sale_price_per_sqft'] = np.nan

    clean['sale_price_per_res_unit'] = clean.sale_price / clean.residential_units
    
    # Strip whitespace for building class category, and split the numeric code from the name
    clean['building_class_category']= clean['building_class_category'].apply(strip_whitespace)

    partitioned = clean['building_class_category'].str.partition(' ')
    clean[['building_class_id', 'building_class_category']] = partitioned.iloc[:, [0,2]]

    # Use the building class ID to get property type
    clean['building_type']=clean['building_class_id'].apply(building_class_to_type)

    # Create a borough name field
    clean['borough_name'] = clean['borough'].map(BOROUGH_MAPPING)
    #clean['borough_name'] = clean['borough'].apply(create_borough_column)
    #clean['boro'] = pd.Categorical.from_codes(clean.borough, BOROUGH_MAPPING)

    #Subset Data
    # columns=['borough_name','zip_code','neighborhood','building_type',
    #          'residential_units','sale_price','log_sale_price',
    #          'sale_price_per_sqft','sale_price_per_res_unit']
    # clean = clean[clean.building_type != None]
    # #clean = clean[(clean.residential_units < 4) ]
   
    # clean=clean[columns]
    return clean


class SalesData(object):


    def __init__(self):
        pass

    def load_rolling_sales_data(self):
        '''Load the rolling sales data into a dataframe'''
        print "Loading rolling sales data..."
        sys.stdout.flush()

        urls = [
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
            ]

        # Create empty list of borough dataframes
        boroughs = list()
        for url in urls:
            print "Loading %s" % url.split('/')[-1]
            sys.stdout.flush()
            boroughs.append(pd.read_excel(url, skiprows=[0,1,2,3]))

        # Concatenate all boroughs together
        self.raw_data = pd.concat(boroughs)
        
        print "Finished loading raw data. Cleaning data..."
        sys.stdout.flush()

        # Clean data and save to class instance
        self.data = clean_data(self.raw_data)
        
        print "Done cleaning data."
        sys.stdout.flush()

        return self.data

    def create_from_scratch(self, database):
        '''Load data, clean, and insert into database'''
        self.load_rolling_sales_data()

        