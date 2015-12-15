'''Module with plotting functions'''

import matplotlib
matplotlib.use('SVG')
import matplotlib.pyplot as plt
import mpld3
import cStringIO
import numpy as np

# Use seaborn if installed
try:
	import seaborn as sns
	# Use seaborn styles to make prettier plots
	sns.set_style('white')
except ImportError:
	pass



class Plotter(object):

	def __init__(self, data, label=''):
		self.data = data
		self.label = label
		# Use seaborn styles to make prettier plots
		sns.set_style('white')
		#self.figure, self.axes = plt.subplots(nrows=2, ncols=3, figsize=(15,9))
		#self.figure.subplots_adjust(wspace=.5, hspace=.5, left=.05, right=.85)
		#print self.axes

	def fig_to_svg(self, figure=None):
		'''Convert the current matplotlib figure to SVG data, to be included in a web page'''
		if figure is None:
			figure = plt.gcf()

		# Use a StringIO stream/buffer to store the figure, rather than writing
		# to a file on disk
		io_buffer = cStringIO.StringIO()
		figure.savefig(io_buffer, format='svg')
		svg_data = io_buffer.getvalue()
		io_buffer.close()

		return svg_data

	def init_fig(self):
		'''Method to initialize a figure object'''
		fig = plt.figure()
		fig.set_size_inches(4, 4)
		return fig

	def price_per_unit_histogram(self):
		'''Plot a histogram of price-per-unit for the zip code in 2015'''
		fig = self.init_fig()
		self.data.loc[self.data.year==2015, 'sale_price_per_res_unit'].hist(xrot=90)
		plt.xlabel("Sale Price")
		plt.ylabel("Sales")
		plt.title("Distribution of Sale Price per Residential Unit\n%s" % self.label, y=1.05)
		plt.tight_layout()
		return self.fig_to_svg()

	def sales_volume_bar_chart(self, groupby='building_type',
								groupbylabel="Building Type"):
		'''Plot a bar chart of sales volume by a groupby variable'''
		fig = self.init_fig()
		units = self.data.loc[self.data.year==2015].groupby(groupby).residential_units.sum()
		plt.barh(np.arange(len(units)), units)
		plt.ylabel(groupbylabel)
		plt.xlabel("Residential Units in Properties Sold", x=0)
		plt.title("Residential Units Sold by %s\n%s" % (groupbylabel, self.label), x=0)
		plt.yticks(np.arange(len(units)) + 0.5, units.index, va='top')
		plt.tight_layout()
		return self.fig_to_svg()

	def sales_volume_year_bar_chart(self):
		'''Plot the sales volume by year'''
		fig = self.init_fig()

		yearly_count = self.data.groupby('year').residential_units.sum()
		plt.bar(np.arange(len(yearly_count)), yearly_count)
		plt.xlabel("Year")
		plt.ylabel("Residential Units in Properties Sold")
		plt.title("Residential units Sold by Year\n%s" % self.label)
		plt.xticks(np.arange(len(yearly_count))+0.5, yearly_count.index, ha='center')
		plt.tight_layout()
		return self.fig_to_svg()

	def sale_price_per_sq_foot_boxplot(self, groupby, title):
		'''Boxplot of sale price per square foot, grouped by a groupby variable'''
		fig = self.init_fig()

		# This figure needs to be extra wide
		fig.set_size_inches(10, 4)

		# Remove missings and restrict to the columns we need
		data = self.data[[groupby, 'sale_price_per_sqft']].dropna()

		# The boxplot function takes a list of Series, so we make one Series for each
		# group, and append them all into a list
		groups = list()
		values = data[groupby].value_counts().index # All the levels of the groupby variable

		for value in values:
			groups.append(data.loc[data[groupby]==value, 'sale_price_per_sqft'])
		
		# Now make the plot
		plt.boxplot(groups, 0, '')
		plt.xticks(np.arange(len(values))+1, values)
		plt.ylabel("Sale Price per Sq. Ft.")
		plt.title(title)
		plt.tight_layout()
		return self.fig_to_svg()





	def all_plots(self):
		return [self.price_per_unit_histogram(),
				self.sales_volume_bar_chart(groupby='building_type', 
											groupbylabel='Building Type'),
				self.sales_volume_year_bar_chart(),
				self.sale_price_per_sq_foot_boxplot('building_type', 
												"Sale Price per Sq. Ft. by Building Type\n%s" % self.label)
				]

	def borough_plots(self):
		return [self.price_per_unit_histogram(),
				self.sales_volume_bar_chart(groupby='borough_name', 
											groupbylabel='Borough'),
				self.sales_volume_year_bar_chart(),
				self.sale_price_per_sq_foot_boxplot('borough_name',
							"Sale Price per Sq. Ft. by Borough\n%s" % self.label)
				]


	def old_plots(self):
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

		imgdata = StringIO.StringIO()
		self.figure.savefig(imgdata, format='svg')
		imgdata.seek(0)  # rewind the data

		svg_dta = imgdata.buf  # this is svg data

		#return mpld3.fig_to_html(self.figure)
		return svg_dta


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