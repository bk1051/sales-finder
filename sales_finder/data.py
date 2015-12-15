'''
Module to manipulate and store data
'''
import pandas as pd
import numpy as np
import sys
from plots import Plotter
from urllib2 import HTTPError
import numbers

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
    newname = fieldname.strip().lower()
    newname = newname.replace(" ", "_")
    newname = newname.replace("-", "")
    return newname


def rename_columns(dataframe):
    '''Clean all the column names in a dataframe'''
    dataframe.columns = [field_cleaner(field) for field in dataframe.columns]


def building_class_to_type(build_id):
    '''Create property type from building class ID codes'''
    single_family = ['01']
    two_three_family = ['02', '03']
    multifamily_rental = ['07', '08', '11A', '14']
    coops = ['09', '10', '17']
    condos = ['4', '12', '13', '15']

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
    clean.loc[clean.gross_square_feet == 0, 'sale_price_per_sqft'] = np.nan

    clean['sale_price_per_res_unit'] = clean.sale_price / clean.residential_units

    # Strip whitespace for building class category, and split the numeric code from the name
    clean['building_class_category'] = clean['building_class_category'].apply(strip_whitespace)

    partitioned = clean['building_class_category'].str.partition(' ')
    clean[['building_class_id', 'building_class_category']] = partitioned.iloc[:, [0, 2]]

    # Use the building class ID to get property type
    clean['building_type'] = clean['building_class_id'].apply(building_class_to_type)

    # Create a borough name field
    clean['borough_name'] = clean['borough'].map(BOROUGH_MAPPING)

    # Clean apartment number
    clean['apartment_number'] = clean['apartment_number'].astype(str)

    # Extract year from sale date
    clean['year'] = clean['sale_date'].apply(lambda d: d.year)

    return clean


class NoResultsException(Exception):
    '''Exception thrown when a query has no results'''
    pass


class SalesData(object):
    '''Class to maintain data in database and manage queries and results.'''


    def __init__(self, database, table="sales", limited_data=False):
        '''Constructor.

        Arguments:
            database = Required SQLAlchemy database object
            table    = Table name to save/load sales data (defaults to 'sales')
            app      = a Flask app instance. Can also be set after creation by calling the 
                        init_app method.
        '''
        self.database = database
        self.table = table
        self.limited_data = limited_data


    def query(self, conditions=None):
        '''Query database with given conditions.

        conditions is a dict of the form {'variable_name': value}.
        Results returned must then satisfy: variable_name = value
        '''
        # Where clause starts empty
        where = ''

        # If any conditions are given, loop through each key/value
        # and build up the where clause
        if conditions is not None:
            condition_strings = list()
            for key, value in conditions.items():
                # Check type to see whether to surround in quotes or not
                if isinstance(value, numbers.Number):
                    condition_strings.append("%s = %s" % (key, value))
                else:
                    condition_strings.append("%s = '%s'" % (key, value))

            where = 'where %s' % " and ".join(condition_strings)

        # Return the results of the query, as a pandas DataFrame
        return pd.read_sql_query("select * from %s %s" % (self.table, where), self.database.engine)



    def query_for_borough(self, borough):
        '''Query Datatbase by borough and store into Dataframe'''
        self.query_borough = pd.read_sql_query("select * from %s where borough=%s" % (self.table, borough), self.database.engine)
        return self.query_borough

    def query_for_zip_code(self, zip_code):
        '''Query database for all rows with a certain zip code, and save in a DataFrame'''
        self.query_zip = pd.read_sql_query("select * from %s where zip_code=%s" % (self.table, zip_code), self.database.engine)
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

    def results_for_zip_code(self, zip_code, year=2015):
        '''Return dictionary of results for zip code'''

        zipdata = self.query({'zip_code': zip_code, 'year': year})


        if len(zipdata) == 0:
            raise NoResultsException()

        # Get borough level results
        borough = zipdata.borough.mode()[0]
        boroughdata = self.query({'borough': borough, 'year': year})

        # Get neighborhood level results
        neighborhood = zipdata.neighborhood.mode()[0]
        neighborhooddata = self.query({'neighborhood': neighborhood, 'year': year})

        # Get citywide results
        citydata = self.query({'year': year})

        zip_results = self.results_for_data(zipdata)
        borough_results = self.results_for_data(boroughdata)
        neighborhood_results = self.results_for_data(neighborhooddata)
        city_results = self.results_for_data(citydata)

        return [{ 'name': "ZIP Code %s" % zip_code,
                    'summary_stats': zip_results },
                { 'name': BOROUGH_MAPPING[borough],
                    'summary_stats': borough_results},
                { 'name': neighborhood.title(),
                    'summary_stats': neighborhood_results},
                { 'name': "New York City",
                    'summary_stats': city_results}]

    def plots_for_zip_code(self, zip_code):
        ''' Return Plots by Zipcode'''
        zipdata = self.query_for_zip_code(zip_code)

        plotter = Plotter(zipdata, "ZIP: %s" % zip_code)
        return plotter.all_plots()

    def plots_for_boroughs(self):
        ''' Return Plots by Borough'''
        plotter = Plotter(self.query())
        return plotter.borough_plots()


    def file_urls(self):
        '''Get list of URLs for files to download'''
        urls = list()
        for year in range(2011, 2015):
            for boro in ['bronx', 'brooklyn', 'manhattan', 'queens', 'statenisland']:
                urls.append(
                    "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/{year}/{year}_{boro}.xls".format(
                            year=year, boro=boro
                        )
                    )
        rolling_urls = [
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
                "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
            ]
        urls.extend(rolling_urls)
        return urls


    def load_sales_data(self):
        '''Load the sales data into a dataframe'''
        print "Loading sales data..."
        sys.stdout.flush()

        # Get list of URLs; if limited_data is set to true, then only download one file.
        # Otherwise, go through and load each one as a dataframe
        urls = self.file_urls()
     
        if self.limited_data:
            # Use only Bronx, the smallest file
            urls = [urls[0], urls[-4]]

        # Create empty list of borough dataframes
        datasets = list()
        for url in urls:
            print "Loading %s" % url.split('/')[-1],
            sys.stdout.flush()
            try:
                dset = pd.read_excel(url, skiprows=[0,1,2,3])
                datasets.append(dset)
                print "{:,} rows".format(len(dset))
            except HTTPError:
                print "COULDN'T DOWNLOAD %s" % url

        print "Finished loading data. Cleaning data..."
        sys.stdout.flush()

        # Concatenate all boroughs together
        cleaned = list()
        for dataset in datasets:
            cleaned.append(clean_data(dataset))

        self.data = pd.concat(cleaned)
        
        
        print "Done cleaning data: {:,} rows.".format(len(self.data))
        print self.data.borough_name.value_counts()
        sys.stdout.flush()

        return self.data

    def create_from_scratch(self):
        '''Load data, clean, and insert into database'''
        self.load_sales_data()

        # Save data to SQL
        print "Saving to database...(table=%s)" % self.table
        sys.stdout.flush()
        self.data.to_sql(self.table, self.database.engine, if_exists='replace')
        print "Done"






