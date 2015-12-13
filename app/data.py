'''
Module to manipulate and store data
'''
import pandas as pd
import numpy as np
import sys
#import matplotlib.pyplot as plt
import mpld3

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


class NoResultsException(Exception):
    '''Exception thrown when a query has no results'''
    pass


class SalesData(object):


    def __init__(self, database, app=None):
        self.database = database
        self.app = app
        if self.app is not None:
            self.init_app(self.app)
        self.query = None

    def init_app(self, app):
        self.app = app

    def query_for_borough(self, borough):
        self.query_borough = pd.read_sql_query("select * from sales where borough=%s" % borough, self.database.engine)
        return self.query_borough

    def query_for_zip_code(self, zip_code):
        '''Query database for all rows with a certain zip code, and save in a DataFrame'''
        self.query_zip = pd.read_sql_query("select * from sales where zip_code=%s" % zip_code, self.database.engine)
        return self.query_zip

    def results_for_data(self, dataframe):
        '''Get summary results for a dataframe'''
        n_sales = len(dataframe)
        med_price = np.median(dataframe.sale_price)
        med_price_unit = np.median(dataframe.sale_price_per_res_unit)
        med_price_sqft = np.median(dataframe.sale_price_per_sqft.dropna())

        return {'Total Number of Sales': "{:,}".format(n_sales),
                'Median Price': "${:,}".format(int(med_price)),
                'Median Price Per Residential Unit': "${:,}".format(int(med_price_unit)),
                'Median Price Per Sq. Foot': "${:,}".format(int(med_price_sqft))
                }

    def results_for_zip_code(self, zip_code):
        '''Return dictionary of results for zip code'''

        zipdata = self.query_for_zip_code(zip_code)


        if len(zipdata) == 0:
            raise NoResultsException()

        # Get borough level results
        borough = zipdata.borough.mode()[0]
        boroughdata = self.query_for_borough(borough)

        zip_results = self.results_for_data(zipdata)
        borough_results = self.results_for_data(boroughdata)

        return [{ 'name': "ZIP Code %s" % zip_code,
                    'summary_stats': zip_results },
                { 'name': BOROUGH_MAPPING[borough],
                    'summary_stats': borough_results}]

    def plots_for_zip_code(self, zip_code):
        zipdata = self.query_for_zip_code(zip_code)

        plot = zipdata.plot(kind='box', title="TITLE",legend=False, rot=0, figsize=(8,5))
        return mpld3.fig_to_html(plot.get_figure())


        


    def load_rolling_sales_data(self):
        '''Load the rolling sales data into a dataframe'''
        print "Loading rolling sales data..."
        sys.stdout.flush()

        urls = [
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
            ]
        if self.app.config['LIMITED_DATA']:
            # Use only Bronx, the smallest file
            urls = urls[1]

        # Create empty list of borough dataframes
        boroughs = list()
        for url in urls:
            print "Loading %s" % url.split('/')[-1]
            sys.stdout.flush()
            boroughs.append(pd.read_excel(url, skiprows=[0,1,2,3]))

        # Concatenate all boroughs together
        self.raw_data = pd.concat(boroughs)
        
        print "Finished loading raw data ({:,} rows). Cleaning data...".format(len(self.raw_data))
        sys.stdout.flush()

        # Clean data and save to class instance
        self.data = clean_data(self.raw_data)
        
        print "Done cleaning data: {:,} rows.".format(len(self.data))
        print self.data.borough_name.value_counts()
        sys.stdout.flush()

        return self.data

    def create_from_scratch(self):
        '''Load data, clean, and insert into database'''
        self.load_rolling_sales_data()

        # Save data to SQL
        print "Saving to database..."
        sys.stdout.flush()
        self.data.to_sql('sales', self.database.engine, if_exists='replace')
        print "Done"
