'''Module with plotting functions'''

import matplotlib
matplotlib.use('SVG')
#import matplotlib.pyplot as plt
import mpld3


class Plotter(object):

	def __init__(self, data):
		self.data = data

	def all_plots(self):

		plot = self.data[['building_type', 'sale_price']].plot(kind='box', title="TITLE")
		return mpld3.fig_to_html(plot.get_figure())


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