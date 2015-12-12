'''
Module to manipulate and store data
'''
import pandas as pd
import numpy as np

def field_cleaner(fieldname):
    newname = fieldname.lower()
    newname = newname.replace(" ", "_")
    newname = newname.replace("-", "")
    return newname


def rename_columns(dataframe):
    dataframe.columns = [field_cleaner(field) for field in dataframe.columns]


import pandas as pd
    urls = [
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_manhattan.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_brooklyn.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_bronx.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_queens.xls",
        "http://www1.nyc.gov/assets/finance/downloads/pdf/rolling_sales/rollingsales_statenisland.xls"
    ]
    df = pd.read_excel(urls[0], skiprows=[0,1,2,3])
    print df.head()
    rename_columns(df)
    df.to_sql('_sales_data', database.engine)


class SalesData(Object):


    def __init__():
        pass

    def load_rolling_sales_data(self):
        '''Load the rolling sales data into a dataframe'''
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
            boroughs.append(pd.read_excel(url, skiprows=[0,1,2,3]))

        # Concatenate all boroughs together
        raw_data = pd.concat(boroughs)
        rename_columns(raw_data)
        self.data = rename_

        return dataframe

    def create_from_scratch(self, database):
        '''Load data, clean, and insert into database'''
        pass