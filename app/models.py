from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, event, Boolean, Table
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relationship


#user_to_user = db.Table('user_to_user', db.metadata,
#	db.Column("left_user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
#	db.Column("right_user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True)
#)

#assigned_users = db.Table('assigned_users', db.metadata,
#	Column('user_id', Integer, ForeignKey('user.id')),
#	Column('load_id', Integer, ForeignKey('load.id'))
#)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	# User authentication information
	#username = db.Column(db.String(50), nullable=False, unique=True)
	password = db.Column(db.String(255), nullable=False, server_default='')
	#reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

	# User email information
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)
	confirmed_at = db.Column(db.DateTime())

	# User information
	authenticated = db.Column(db.Boolean(), nullable=False, server_default='0')
	company_name = db.Column(db.String(100), nullable=False, server_default='')
	#brokered_loads = db.relationship('Load', backref='broker', lazy='dynamic', foreign_keys='Load.broker_id')
	#assigned_loads = db.relationship('Load', backref='carrier', lazy='dynamic', foreign_keys='Load.carrier_id')
	#fleet = db.relationship("Fleet", uselist=False, backref="carrier")
	#contacts = db.relationship("User",
	#				secondary=user_to_user,
	#				primaryjoin=id==user_to_user.c.left_user_id,
	#				secondaryjoin=id==user_to_user.c.right_user_id,
	#				backref="contacted_by"
    #)
	roles = db.relationship('Role')


	def __init__(self, email, company_name, password):
		self.email = email
		self.company_name = company_name
		self.set_password(password)
		self.fleet = Fleet()

	def is_carrier(self):
		return len(filter((lambda role: role.name == 'carrier'), self.roles)) == 1

	def get_id(self):
		return self.email

	def is_active(self):
		#True, as all users are active.
		return True

	def is_authenticated(self):
		#"""Return True if the user is authenticated."""
		return self.authenticated

	def is_anonymous(self):
		#False, as anonymous users aren't supported."""
		return False

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def __repr__(self):
		return '<User %r>' % (self.company_name)

#class Load(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	name = db.Column(db.String(80), index=True)
#	status = db.Column(db.String(20))
#	lane = db.relationship("Lane", uselist=False, backref="load")
#	load_detail = db.relationship("LoadDetail", uselist=False, backref="load")
#	broker_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	carrier_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	bids = db.relationship('Bid', backref='load')
#	carrier_cost = db.Column(db.Float(3))
#	price = db.Column(db.Float(3))
#	description = db.Column(db.String(250))
#	driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
#	assigned_driver = db.relationship("Driver", backref="loads")
#	
#	def __repr__(self):
#		return '<User %r>' % (self.name)
#
#class Bid(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	load_id = Column(Integer, ForeignKey('load.id'))
#	offered_by_id = Column(db.Integer, db.ForeignKey('user.id'))
#	offered_to_id = Column(db.Integer, db.ForeignKey('user.id'))
#	offered_by = relationship("User", foreign_keys=offered_by_id)
#	offered_to = relationship("User", backref="offered_bids", foreign_keys=offered_to_id)
#	value = db.Column(db.Float(3))
#	status = db.Column(db.String(10))
#
#class LoadDetail(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	weight = db.Column(db.Integer)
#	dim_length = db.Column(db.Integer)
#	dim_width = db.Column(db.Integer)
#	dim_height = db.Column(db.Integer)
#	approx_miles = db.Column(db.Integer)
#	number_pieces = db.Column(db.Integer)
#	comments = db.Column(db.String(500))
#	load_id = db.Column(Integer, ForeignKey('load.id'))
#	pickup_date = db.Column(db.Date) 
#	delivery_date = db.Column(db.Date)
#	trailer_group = db.Column(db.String(20))
#	trailer_type = db.Column(db.String(20))
#	load_type = db.Column(db.String(20))
#	total_miles = db.Column(db.Integer) 
#	purchase_order = db.Column(db.String(20))
#	over_dimensional = db.Column(db.Boolean)
#
#
#class Lane(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	load_id = db.Column(Integer, ForeignKey('load.id'))
#	origin_id = db.Column(db.Integer, db.ForeignKey('location.id'))
#	destination_id = db.Column(db.Integer, db.ForeignKey('location.id'))
#	origin = db.relationship("Location", backref="origin_lanes", foreign_keys=origin_id)
#	destination = db.relationship("Location", backref="destination_lanes", foreign_keys=destination_id)
#	#locations = db.relationship('Location', backref='lane', lazy='dynamic')
#
#
#class Location(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	#lane_id = db.Column(db.Integer, db.ForeignKey('lane.id'))
#	address1 = db.Column(db.String(100))
#	address2 = db.Column(db.String(100))
#	city = db.Column(db.String(100))
#	state = db.Column(db.String(80))
#	postal_code = db.Column(db.Integer)
#	latitude = db.Column(db.Float(6))
#	longitude = db.Column(db.Float(6))
#	contact_name = db.Column(db.String(60))
#	contact_email = db.Column(db.String(30))
#	contact_phone = db.Column(db.String(30))
#
#	contact_phone_area_code = db.Column(db.String(3))
#	contact_phone_prefix = db.Column(db.String(3))
#	contact_phone_line_number = db.Column(db.String(4))
#
#	def __repr__(self):
#		return '%s, %s' % (self.city, self.state)
#
#class Fleet(db.Model):
#	id = db.Column(db.Integer, primary_key=True)
#	user_id = db.Column(Integer, ForeignKey('user.id'))
#	trucks = db.relationship('Truck', backref='fleet', lazy='dynamic')
#	drivers = db.relationship('Driver', backref='fleet', lazy='dynamic')
#
#
#class Truck(db.Model):
#	id = db.Column(db.Integer, primary_key = True)
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	fleet_id = db.Column(Integer, ForeignKey('fleet.id'))
#	driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
#	name = db.Column(db.String(100))
#	latitude = db.Column(db.Float(6))
#	longitude = db.Column(db.Float(6))
#	is_available = db.Column(db.Boolean)
#	trailer_group = db.Column(db.String(30))
#	trailer_type = db.Column(db.String(30))
#	max_weight = db.Column(db.Integer)
#	dim_length = db.Column(db.Integer)
#	dim_height = db.Column(db.Integer)
#	dim_width = db.Column(db.Integer)
#
#class Driver(db.Model):
#	id = db.Column(db.Integer, primary_key = True)
#	fleet_id = db.Column(db.Integer, ForeignKey('fleet.id'))
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#	first_name = db.Column(db.String(30))
#	last_name = db.Column(db.String(30))
#	phone_area_code = db.Column(db.String(3))
#	phone_prefix = db.Column(db.String(3))
#	phone_line_number = db.Column(db.String(4))
#	truck = db.relationship("Truck", uselist=False, backref="driver")
#
#	def get_phone_number(self):
#		return "1 (" + str(self.phone_area_code) + ")-" + str(self.phone_prefix) +"-" + str(self.phone_line_number)
#	def get_full_name(self):
#		return self.first_name + " " + self.last_name
#
class Role(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	user_id = db.Column(db.String, db.ForeignKey('User.id'))
