from app import app
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, event, Boolean, Table
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relationship
from datetime import datetime

User_to_User = db.Table('user_to_user', db.metadata,
	db.Column('left_user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
	db.Column('right_user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
)

#assigned_Users = db.Table('assigned_Users', db.metadata,
#	Column('User_id', Integer, ForeignKey('User.id')),
#	Column('load_id', Integer, ForeignKey('Load.id'))
#)

assigned_Contacts = db.Table('assigned_Contacts', db.metadata,
	Column('Contact_id', Integer, ForeignKey('Contact.id')),
	Column('load_id', Integer, ForeignKey('Load.id'))
)

class Lead(db.Model):
	__tablename__ = 'Lead'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)

class User(db.Model):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key=True)
	# User authentication information
	#Username = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(255), nullable=False, server_default='')
	#reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

	# User email information
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)
	confirmed_at = db.Column(db.DateTime())

	# User information
	authenticated = db.Column(db.Boolean(), nullable=False, server_default='0')
	company_name = db.Column(db.String(100), nullable=False, server_default='')

	loads = db.relationship('Load', backref='created_by', lazy='dynamic', foreign_keys='Load.user_id')
	
	fleet = db.relationship('Fleet', uselist=False, backref='carrier')
	#contacts = db.relationship('User',
	#				secondary=User_to_User,
	#				primaryjoin=id==User_to_User.c.left_user_id,
	#				secondaryjoin=id==User_to_User.c.right_user_id,
	#				backref='contacted_by'
    #)
	roles = db.relationship('Role')
	customer_id = db.Column(db.Integer)


	def __init__(self, email, company_name, password):
		self.email = email
		self.company_name = company_name
		self.set_password(password)
		self.fleet = Fleet()

	def is_carrier(self):
		return len(filter((lambda role: role.name == 'carrier'), self.roles)) == 1

	def get_id(self):
		return self.id

	def is_active(self):
		#True, as all Users are active.
		return True

	def is_authenticated(self):
		#'Return True if the User is authenticated.'
		return self.authenticated

	def is_anonymous(self):
		#False, as anonymous Users aren't supported.'
		return False

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def activate(self):
		self.confirmed_at = datetime.now()

	def is_confirmed(self):
		return self.confirmed_at is not None

	def __repr__(self):
		return '<User %r>' % (self.company_name)

class Load(db.Model):
	__tablename__ = 'Load'
	id = db.Column(db.Integer, primary_key=True)
	#referencing classes
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

	broker_id = db.Column(db.Integer, db.ForeignKey('Contact.id'))
	shipper_id = db.Column(db.Integer, db.ForeignKey('Contact.id'))

	#general
	name = db.Column(db.String(80), index=True)
	status = db.Column(db.String(20))
	trailer_group = db.Column(db.String(20))
	trailer_type = db.Column(db.String(20))
	load_type = db.Column(db.String(20))
	total_miles = db.Column(db.Integer) 
	purchase_order = db.Column(db.String(20))
	over_dimensional = db.Column(db.Boolean)
	carrier_cost = db.Column(db.Float(3))
	price = db.Column(db.Float(3))
	description = db.Column(db.String(250))
	comments = db.Column(db.String(500))

	

	#children
	lane = db.relationship('Lane', uselist=False, backref='load')
	bids = db.relationship('Bid', backref='load')

	#assignments
	driver_id = db.Column(db.Integer, db.ForeignKey('Driver.id'))
	assigned_driver = db.relationship('Driver', backref='loads')
	
	
	def __repr__(self):
		return '<User %r>' % (self.name)

class Bid(db.Model):
	__tablename__ = 'Bid'
	id = db.Column(db.Integer, primary_key=True)
	load_id = Column(db.Integer, db.ForeignKey('Load.id'))
	offered_by_id = Column(db.Integer, db.ForeignKey('User.id'))
	offered_to_id = Column(db.Integer, db.ForeignKey('User.id'))
	offered_by = db.relationship('User', foreign_keys=offered_by_id)
	offered_to = db.relationship('User', backref='offered_bids', foreign_keys=offered_to_id)
	value = db.Column(db.Float(3))
	status = db.Column(db.String(10))

class Lane(db.Model):
	__tablename__ = 'Lane'
	id = db.Column(db.Integer, primary_key=True)
	load_id = db.Column(Integer, ForeignKey('Load.id'))
	locations = db.relationship('Location', backref='lane', lazy='dynamic')


class Location(db.Model):
	__tablename__ = 'Location'
	id = db.Column(db.Integer, primary_key=True)
	lane_id = db.Column(db.Integer, db.ForeignKey('Lane.id'))
	contact_id = db.Column(db.Integer, db.ForeignKey('Contact.id'))
	
	address = db.relationship('Address', uselist=False, backref='location')

	pickup_id = db.Column(db.Integer, db.ForeignKey('LoadDetail.id'))
	pickup_details = db.relationship('LoadDetail', primaryjoin="LoadDetail.id==Location.pickup_id")

	delivery_id = db.Column(db.Integer, db.ForeignKey('LoadDetail.id'))
	#delivery_details_id = db.Column(db.Integer, db.ForeignKey('loaddetail.id'))
	delivery_details = db.relationship('LoadDetail', primaryjoin="LoadDetail.id==Location.delivery_id")

	stop_number = db.Column(db.Integer)
	arrival_date = db.Column(db.Date)

	type = db.Column(db.String(10))
	status = db.Column(db.String(20))
	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))

	def __repr__(self):
		return '%s, %s' % (self.city, self.state)

class LoadDetail(db.Model):
	__tablename__ = 'LoadDetail'
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(10))
	weight = db.Column(db.Integer)
	dim_length = db.Column(db.Integer)
	dim_width = db.Column(db.Integer)
	dim_height = db.Column(db.Integer)
	approx_miles = db.Column(db.Integer)
	number_pieces = db.Column(db.Integer)
	notes = db.Column(db.String(500))

class Address(db.Model):
	__tablename__ = 'Address'
	id = db.Column(db.Integer, primary_key=True)
	location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))
	address1 = db.Column(db.String(100))
	address2 = db.Column(db.String(100))
	city = db.Column(db.String(100))
	state = db.Column(db.String(80))
	postal_code = db.Column(db.Integer)
	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))

class Contact(db.Model):
	__tablename__ = 'Contact'
	id = db.Column(db.Integer, primary_key=True)
	location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))
	#contacts = db.relationship('User',
	#				secondary=User_to_User,
	#				primaryjoin=id==User_to_User.c.left_user_id,
	#				secondaryjoin=id==User_to_User.c.right_user_id,
	#				backref='contacted_by'
    #)
	brokered_loads = db.relationship('Load', backref='broker', lazy='dynamic', foreign_keys='Load.broker_id')
	shipped_loads = db.relationship('Load', backref='shipper', lazy='dynamic', foreign_keys='Load.shipper_id')
	location_contact = db.relationship('Location', backref='contact', lazy='dynamic', foreign_keys='Location.contact_id')
	name = db.Column(db.String(60))
	email = db.Column(db.String(30))
	phone = db.Column(db.String(30))

	phone_area_code = db.Column(db.String(3))
	phone_prefix = db.Column(db.String(3))
	phone_line_number = db.Column(db.String(4))

class Fleet(db.Model):
	__tablename__ = 'Fleet'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, ForeignKey('User.id'))
	trucks = db.relationship('Truck', backref='Fleet', lazy='dynamic')
	drivers = db.relationship('Driver', backref='Fleet', lazy='dynamic')


class Truck(db.Model):
	__tablename__ = 'Truck'
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	fleet_id = db.Column(db.Integer, ForeignKey('Fleet.id'))
	driver_id = db.Column(db.Integer, db.ForeignKey('Driver.id'))
	name = db.Column(db.String(100))
	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))
	is_available = db.Column(db.Boolean)
	trailer_group = db.Column(db.String(30))
	trailer_type = db.Column(db.String(30))
	max_weight = db.Column(db.Integer)
	dim_length = db.Column(db.Integer)
	dim_height = db.Column(db.Integer)
	dim_width = db.Column(db.Integer)

class Driver(db.Model):
	__tablename__ = 'Driver'
	id = db.Column(db.Integer, primary_key = True)
	fleet_id = db.Column(db.Integer, ForeignKey('Fleet.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	email = db.Column(db.String(255))
	phone_area_code = db.Column(db.String(3))
	phone_prefix = db.Column(db.String(3))
	phone_line_number = db.Column(db.String(4))
	truck = db.relationship('Truck', uselist=False, backref='driver')

	def get_phone_number(self):
		return '1 (' + str(self.phone_area_code) + ')-' + str(self.phone_prefix) +'-' + str(self.phone_line_number)

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

class Role(db.Model):
	__tablename__ = 'Role'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
