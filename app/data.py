'''
Module to manipulate and store data
'''
import pandas as pd
import numpy as np
import sys
import matplotlib
matplotlib.use('SVG')
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

    # Clean apartment number
    clean['apartment_number'] = clean['apartment_number'].astype(str)
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


    def __init__(self, database, table="sales", app=None):
        '''Constructor.

        Arguments:
            database = Required SQLAlchemy database object
            table    = Table name to save/load sales data (defaults to 'sales')
            app      = a Flask app instance. Can also be set after creation by calling the init_app method.
        '''
        self.database = database
        self.table = table
        self.init_app(app)
        self.query = None

    @property
    def app(self):
        '''Getter for app property. Since SalesData can be created without an app object,
        we want to make sure it is never called while still set to None. This checks that
        it is not none when it is accessed.'''
        if self._app is None:
            raise NoAppObjectError("SalesData has no Flask app object. Need to specify it in constructor or call init_app.")
        return self._app

    def init_app(self, app):
        '''Attach app instance to SalesData instance'''
        self._app = app

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

        plot = zipdata['building_type'].plot(kind='box', title="TITLE",legend=False, rot=0, figsize=(8,5))
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
            urls = [urls[1]]

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
        print "Saving to database...(table=%s)" % self.table
        sys.stdout.flush()
        self.data.to_sql(self.table, self.database.engine, if_exists='replace')
        print "Done"







def graph_count_sales(dataframe):
    df=dataframe
    df=df[['building_type','residential_units']]
    df=df.groupby('building_type').sum().reset_index()
    
    #Sort Columns 
    building_type= ['CONDOS', 'COOPS', 'ONE FAMILY HOMES', 'TWO FAMILY HOMES', 'THREE FAMILY HOMES']
    mapping = {building_type: i for i, building_type in enumerate(building_type)}
    key = df['building_type'].map(mapping)    
    df = df.iloc[key.argsort()]
    
    
    df=df.plot(kind='bar', title='Total Number of Residential Units Sold',legend=False, rot=0, figsize=(8,5), x='building_type')
    df.set_ylabel("Units Sold", fontsize= 12)
    df.set_xlabel("Residential Classification", fontsize= 12)
    

def graph_mean_sales(dataframe,label,title,x_title):
    df=dataframe
    df=df[['building_type',label]]
    df=df.groupby('building_type').mean().reset_index()
    
    
    building_type= ['CONDOS', 'COOPS', 'ONE FAMILY HOMES', 'TWO FAMILY HOMES', 'THREE FAMILY HOMES']
    mapping = {building_type: i for i, building_type in enumerate(building_type)}
    key = df['building_type'].map(mapping)    
    df = df.iloc[key.argsort()]
    
    
    df=df.plot(kind='barh', title=title,legend=False, rot=0, figsize=(8,5), x='building_type')
    df.set_ylabel('Residential Classfication', fontsize= 12)
    df.set_xlabel(x_title, fontsize= 12)
    
def graph_box(dataframe,label,title,x_title,y_title):
    df=dataframe
    df=df[['building_type',label]]
    #df = df.unstack("building_type")
    df=df.plot(kind='box', title=title,legend=False, rot=0, figsize=(8,5))
    df.set_ylabel(y_title, fontsize= 12)
    df.set_xlabel(x_title, fontsize= 12)
