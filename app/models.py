'''
This file contains the specifications for our database tables
'''

from . import db


class Sale(db.Model):
	__tablename__ = 'sales'
	id = db.Column(db.Integer, primary_key=True)
	borough = db.Column(db.String(13))
	neighborhood = db.Column(db.String(30))
	building_class_category = db.Column(db.String(50))
	tax_class_at_present = db.Column(db.String(2))
	block = db.Column(db.SmallInteger)
	lot = db.Column(db.SmallInteger)
	easement = db.Column(db.SmallInteger)
	building_class_at_present = db.Column(db.String(2))
	address = db.Column(db.String(255))
	apartment_number = db.Column(db.String(10))
	zip_code = db.Column(db.String(5))
	residential_units = db.Column(db.SmallInteger)
	commercial_units = db.Column(db.SmallInteger)
	total_units = db.Column(db.SmallInteger)
	land_square_feet = db.Column(db.Integer)
	gross_square_feet = db.Column(db.Integer)
	year_built = db.Column(db.SmallInteger)
	tax_class_at_time_of_sale = db.Column(db.String(2))
	building_class_at_time_of_sale = db.Column(db.String(2))
	sale_price = db.Column(db.Integer)
	sale_date = db.Column(db.Date)

	def __repr__(self):
		return '<Sale %r - %r - %r>' % (self.id, self.address, self.sale_date)

