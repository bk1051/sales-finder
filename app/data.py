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

    print raw_data.columns

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

    # Clean apartment number
    clean['apartment_number'] = clean['apartment_number'].astype(str)

    clean['year'] = clean['sale_date'].apply(lambda d: d.year)
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

class NoAppObjectError(Exception):
    '''Exception thrown when an app object has not been set.'''


class SalesData(object):


    def __init__(self, database, table="sales", limited_data=False):
        '''Constructor.

        Arguments:
            database = Required SQLAlchemy database object
            table    = Table name to save/load sales data (defaults to 'sales')
            app      = a Flask app instance. Can also be set after creation by calling the init_app method.
        '''
        self.database = database
        self.table = table
        self.limited_data = limited_data
        #self.init_app(app)
        #self.query = None

    # @property
    # def app(self):
    #     '''Getter for app property. Since SalesData can be created without an app object,
    #     we want to make sure it is never called while still set to None. This checks that
    #     it is not none when it is accessed.'''
    #     if self._app is None:
    #         raise NoAppObjectError("SalesData has no Flask app object. Need to specify it in constructor or call init_app.")
    #     return self._app

    # def init_app(self, app):
    #     '''Attach app instance to SalesData instance'''
    #     self._app = app


    def query(self, conditions=None):
        where = ''
        if conditions is not None:
            condition_strings = list()
            for key, value in conditions.items():
                # Check type to see whether to surround in quotes or not
                if isinstance(value, numbers.Number):
                    condition_strings.append("%s = %s" % (key, value))
                else:
                    condition_strings.append("%s = '%s'" % (key, value))
            where = 'where %s' % " and ".join(condition_strings)
        return pd.read_sql_query("select * from %s %s" % (self.table, where), self.database.engine)

    # def query(self, field=None, value=None):
    #     '''Run a query on the database, and return result in DataFrame'''
    #     if field is None or value is None: # Return whole database
    #         return pd.read_sql_query("select * from %s" % self.table, self.database.engine)
    #     else:
    #         return pd.read_sql_query("select * from %s where %s=%s" % (self.table, field, value), self.database.engine)

    def query_for_borough(self, borough):
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

        #zipdata = self.query(field='zip_code', value=zip_code)
        zipdata = self.query({'zip_code': zip_code, 'year': year})


        if len(zipdata) == 0:
            raise NoResultsException()

        # Get borough level results
        borough = zipdata.borough.mode()[0]
        boroughdata = self.query({'borough': borough, 'year': year})

        # Get neighborhood level results
        neighborhood = zipdata.neighborhood.mode()[0]
        #neighborhooddata = self.query(field='neighborhood', value=neighborhood)
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
        zipdata = self.query_for_zip_code(zip_code)

        plotter = Plotter(zipdata, ", ZIP: %s" % zip_code)
        #plot = zipdata['building_type'].plot(kind='box', title="TITLE",legend=False, rot=0, figsize=(8,5))
        #return mpld3.fig_to_html(plot.get_figure())
        return plotter.all_plots()

    def plots_for_boroughs(self):
        plotter = Plotter(self.data)
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
        # urls = [
        #         "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
        #         "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
        #         "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
        #         "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
        #         "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
        #     ]
        #if self.app.config['LIMITED_DATA']:
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
            #print dataset.columns
            #print dataset.describe().T
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






