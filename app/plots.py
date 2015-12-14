'''Module with plotting functions'''

import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt
import mpld3


class Plotter(object):

	def __init__(self, data):
		self.data = data
		self.figure, self.axes = plt.subplots(nrows=2, ncols=3, figsize=(15,9))
		self.figure.subplots_adjust(wspace=.5, hspace=.5, left=.05, right=.85)
		#print self.axes

	def all_plots(self):

		self.axes[0,0].set_title("Distribution of Sale Price Per Unit")
		#
		counts, bins, patches = self.axes[0,0].hist(
			self.data.loc[self.data.year==2015, 'sale_price_per_res_unit'].tolist()
		)
		self.axes[0,0].set_xticklabels(bins, rotation=45)
		self.axes[0,0].set_visible(False)
		# self.axes[0,0].hist(
		# 	self.data.loc[self.data.year==2015, 'sale_price_per_res_unit'].tolist()
		# )

		self.axes[0,0].set_xlabel("TEST")

		#self.axes[0,0].set_xticklabels(self.axes[0,0].get_xticklabels(), rotation=90)
		plt.sca(self.axes[0,0])
		#locs, labels = plt.xticks()
		#self.axes[0,0].set_xticklabels(labels, rotation=45)
		#print locs, labels
		plt.xlabel("Sale Price")
		plt.ylabel("Number of Sales")

		yearly_count = self.data.groupby('year').residential_units.sum()
		print yearly_count
		yearly_count.plot(kind='bar', x='year', ax=self.axes[1,0])
		plt.sca(self.axes[1,0])
		labels = self.axes[1,0].get_xticklabels()
		for label in labels:
			print label
			label.set_rotation('vertical')
		locs, labels = plt.xticks()
		print locs, labels
		plt.xticks(locs, yearly_count.index)
		plt.xlabel("Year")
		plt.ylabel("Residential Units Sold")

		#self.figure = plt.gcf()
		#self.figure.set_size_inches(15, 6)
		# hist = self.axes[0,0].hist(self.data['sale_price_per_res_unit'])

		# type_counts = self.data.groupby('building_type').residential_units.sum()
		# #self.axes[0, 2].bar(range(len(type_counts.building_type)), type_counts.residential_units)
		# type_counts.plot(kind='bar', ax=self.axes[0,2])

		# self.axes[0,2].set_title('Number of Residential Units Sold by Building Type')
		# self.axes[0,2].set_xlabel("Building Type")
		# self.axes[0,2].set_ylabel("Residential Units")

		# plot = self.data[['building_type', 'log_sale_price']].plot(
		# 			kind='box', title="TITLE", by='building_type', ax=self.axes[0,1])
		return mpld3.fig_to_html(self.figure)


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