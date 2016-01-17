from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app, jsonify, abort
from app import app
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, event, Boolean, Table
from sqlalchemy.orm import scoped_session, sessionmaker, backref, relationship
from datetime import datetime
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired, base64_decode, base64_encode)
import urllib
import urllib2
import json
from datetime import datetime

Company_to_Load = db.Table('company_to_load', db.metadata,
	db.Column('company_id', db.Integer, db.ForeignKey('Company.id'), primary_key=True),
	db.Column('load_id', db.Integer, db.ForeignKey('Load.id'), primary_key=True)
)

User_to_Role = db.Table('user_to_role', db.metadata,
	db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
	db.Column('role_id', db.Integer, db.ForeignKey('Role.id'), primary_key=True)
)

User_to_User = db.Table('user_to_user', db.metadata,
	db.Column('left_user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
	db.Column('right_user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
)

detail_to_BOL = Table('detail_to_BOL', db.metadata,
    Column('detail_id', db.Integer, ForeignKey('LoadDetail.id')),
    Column('BOL_id', db.Integer, db.ForeignKey('BOL.id'))
)

location_to_BOL = Table('location_to_BOL', db.metadata,
    db.Column('location_id', db.Integer, ForeignKey('Location.id')),
    db.Column('BOL_id', db.Integer, db.ForeignKey('BOL.id'))
)

#assigned_Users = db.Table('assigned_Users', db.metadata,
#	Column('User_id', Integer, ForeignKey('User.id')),
#	Column('load_id', Integer, ForeignKey('Load.id'))
#)

assigned_Contacts = db.Table('assigned_Contacts', db.metadata,
	Column('Contact_id', Integer, ForeignKey('Contact.id')),
	Column('load_id', Integer, ForeignKey('Load.id'))
)

class Company(db.Model):
	__tablename__ = 'Company'
	id = db.Column(db.Integer, primary_key=True)
	mco = db.Column(db.String, unique=True)
	name = db.Column(db.String(100), nullable=False, server_default='')
	address = db.relationship("Address", uselist=False)
	users = db.relationship("User", backref="company")
	company_type = db.Column(db.String(100), nullable=False, server_default='')

	loads = db.relationship("Load",
                    secondary=Company_to_Load,
                    backref="assigned_companies")#,
	
	fleet = db.relationship('Fleet', uselist=False, backref='company')

	def __repr__(self):
		return '%s' % (self.name)

	def __init__(self, mco, name, address, company_type):
		self.mco = mco
		self.name = name
		self.address=address
		self.company_type=company_type
		self.fleet = Fleet()
		self.loads = []
		self.users = []

	def is_carrier(self):
		return self.company_type == "carrier"

	@staticmethod
	def createCompanyFromForm(form):
		address = Address.createAddressFromForm(form)
		company = Company(mco=form.mco.data, 
							name=form.company_name.data,
							address=address,
							company_type=form.account_type.data)
		db.session.add(company)
		db.session.commit()

	@staticmethod
	def createCompanyFromJSON(json):
		roleCode = json.get('type')
		company = None
		address = Address.createAddressFromJSON(json)
		if roleCode == "owner_operator":
			company = Company(mco=json.get('mco'), 
							name=json.get('companyName'),
							address=address,
							company_type="Owner Operator")
		elif roleCode == "broker" or roleCode == "shipper":
			company = Company(mco=json.get('mco'), 
							name=json.get('companyName'),
							address=address,
							company_type="Shipper/Broker")
		else:
			company = Company(mco=json.get('mco'), 
							name=json.get('companyName'),
							address=address,
							company_type="Carrier")
		return company

	@staticmethod
	def findCompanyByMCO(mco):
		return Company.query.filter_by(mco=mco).first()

class User(db.Model):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key=True)

	#Foreign key to company
	company_id = db.Column(db.Integer, db.ForeignKey('Company.id'))

	# User authentication information
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)
	password = db.Column(db.String(255), nullable=False, server_default='')
	#reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

	
	confirmed_at = db.Column(db.DateTime())

	# User information
	authenticated = db.Column(db.Boolean(), nullable=False, server_default='0')
	first_name = db.Column(db.String(100), nullable=False, server_default='')
	last_name = db.Column(db.String(100), nullable=False, server_default='')
	phone = db.Column(db.String(30))

	#Is account disabled
	disabled = db.Column(db.Boolean)

	#User Roles
	roles = db.relationship("Role",
                    secondary=User_to_Role)

	#Stripe Customer Identier
	customer_id = db.Column(db.Integer)

	def __init__(self, email, first_name, last_name, phone, password):
		self.email = email.lower()
		self.first_name = first_name
		self.last_name = last_name
		self.phone = phone
		if password != "":
			self.set_password(password)

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

	def hash_password(self, password):
		self.password = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password)

	def activate(self):
		self.confirmed_at = datetime.now()

	def is_confirmed(self):
		return self.confirmed_at is not None

	def is_company_admin(self):
		return len(filter((lambda role: role.code == 'company_admin'), self.roles)) > 0

	def is_admin(self):
		return len(filter((lambda role: role.code == 'admin'), self.roles)) > 0

	def isOwnerOperator(self):
		return len(filter(lambda role: role.code == "owner_operator", user.roles)) > 0

	def generate_auth_token(self, expiration=1892160000):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	def makeCompanyAdmin(self):
		role = Role.query.filter_by(code='company_admin').first()
		self.roles.append(role)

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None    # valid token, but expired
		except BadSignature:
			return None    # invalid token
		user = User.query.get(data['id'])
		return user

	@staticmethod
	def createUserFromForm(form):
		user = User(first_name=form.first_name.data,
				last_name=form.last_name.data,
				phone=form.phone_number.data,
				email=form.email.data,
				password=form.password.data)
		db.session.add(user)
		db.session.commit()
		return user

	@staticmethod
	def createUserFromJSON(json):
		user = User(first_name=request.json.get('firstName'),
				last_name=request.json.get('lastName'),
				phone=request.json.get('phoneNumber'),
				email=request.json.get('email'),
				password=request.json.get('password'))
		db.session.add(user)
		db.session.commit()
		return user

	@staticmethod
	def getUserByEmail(email):
		return User.query.filter_by(email=email.lower()).first()

	@staticmethod
	def getUserByID(email):
		return User.query.get_or_404(user_id)

	@staticmethod
	def getUserByActivationSlug(activation_slug):
		s = get_serializer()
		try:
			user_id = s.loads(activation_slug)
		except BadSignature:
			abort(404)

		user = User.query.get_or_404(user_id)
		return user

	def __repr__(self):
		return '%s %s' % (self.first_name, self.last_name)

class Address(db.Model):
	__tablename__ = 'Address'
	id = db.Column(db.Integer, primary_key=True)
	location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))
	company_id = db.Column(db.Integer, ForeignKey('Company.id'))
	address1 = db.Column(db.String(100))
	address2 = db.Column(db.String(100))
	city = db.Column(db.String(100))
	state = db.Column(db.String(80))
	postal_code = db.Column(db.String(10))
	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))

	def __init__(self, address1, city, state, postal_code):
		self.address1 = address1
		self.city = city
		self.state = state
		self.postal_code = postal_code

	@staticmethod
	def createAddressFromForm(form):
		address = Address(address1=form.address1.data,
							city=form.city.data,
							state=form.state.data,
							postal_code=form.postal_code.data)
		db.session.add(address)
		db.session.commit()
		return address 

	@staticmethod
	def createAddressFromJSON(json):
		address = Address(address1=json.get('streetAddress'),
							city=json.get('city'),
							state=json.get('state'),
							postal_code=json.get('postalCode'))

	def __repr__(self):
		if self.address1 is None or self.address1 == "":
			return self.city + ", " + self.state + " " + self.postal_code
		else:
			return self.address1 + ", " + self.city + ", " + self.state + " " + self.postal_code

class Role(db.Model):
	__tablename__ = 'Role'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	code = db.Column(db.String(100))

	@staticmethod
	def findRoleByType(type):
		return Role.query.filter_by(code=type).first()

	def __repr__(self):
		return '%s' % (self.name)

class Lead(db.Model):
	__tablename__ = 'Lead'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)

class Load(db.Model):
	__tablename__ = 'Load'
	id = db.Column(db.Integer, primary_key=True)
	#referencing classes

	broker_id = db.Column(db.Integer, db.ForeignKey('Contact.id'))
	shipper_id = db.Column(db.Integer, db.ForeignKey('Contact.id'))

	#general
	name = db.Column(db.String(80), index=True)
	status = db.Column(db.String(150))
	trailer_group = db.Column(db.String(150))
	trailer_type = db.Column(db.String(150))
	load_type = db.Column(db.String(150))
	total_miles = db.Column(db.Integer) 
	#purchase_order = db.Column(db.String(20))
	over_dimensional = db.Column(db.Boolean, nullable=True)
	carrier_invoice = db.Column(db.String(150))
	broker_invoice = db.Column(db.String(150))
	description = db.Column(db.String(250))
	comments = db.Column(db.String(500))

	max_weight = db.Column(db.String(7), nullable=True)
	max_width = db.Column(db.String(7), nullable=True)
	max_width_type = db.Column(db.String(7), nullable=True)
	max_length = db.Column(db.String(7), nullable=True)
	max_length_type = db.Column(db.String(7), nullable=True)
	max_height = db.Column(db.String(7), nullable=True)
	max_height_type = db.Column(db.String(7), nullable=True)

	tracker = db.relationship("LongLat", lazy='dynamic')
	

	#children
	lane = db.relationship('Lane', uselist=False, backref='load')

	#assignments
	truck_id = db.Column(db.Integer, db.ForeignKey('Truck.id'))
	truck = db.relationship('Truck', backref='loads')

	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	created_by = db.relationship("User")

	bids = db.relationship("Bid", backref="load")

	@staticmethod
	def createLoadFromForm(form, user):
		broker = None
		shipper = None
		load = Load(broker=broker,
					shipper=shipper,
					name=form.name.data, 
					broker_invoice=0, 
					description="",
					over_dimensional=form.over_dimensional.data,
					trailer_type=form.trailer_type.data,
					load_type=form.load_type.data,
					total_miles=form.total_miles.data,
					max_weight=form.max_weight.data,
					max_length=form.max_length.data,
					max_length_type=form.max_length_type.data,
					max_width=form.max_width.data,
					max_width_type=form.max_width_type.data,
					max_height=form.max_height.data,
					max_height_type=form.max_height_type.data)

		load.created_by = user

		load.assigned_driver = None

		stop_off_locations = []
		locations = filter(lambda location: not location.retired == "0", form.locations)
		for location in locations:
			stop_off = Location.createLocationFromForm(location)
			bols = []
			for cur_BOL in filter(lambda b: not b.retired == "0", location.BOLs):
				bol = None
				if stop_off.stop_type == "Drop Off":
					print("finding dropoff")
					print(filter((lambda loc: loc.stop_type == "Pickup"), stop_off_locations))
					bol = Location.findMatchingBOLByNumber(filter((lambda loc: loc.stop_type == "Pickup"), stop_off_locations), cur_BOL)
					print(bol)
				else:				
					print("adding new")
					bol = BOL.createBOLFromForm(cur_BOL)
					print(bol)
				stop_off.BOLs.append(bol)
			db.session.add(stop_off)
			stop_off_locations.append(stop_off)
			

		load.lane = Lane.createLaneFromLocationArray(stop_off_locations)
		db.session.add(load)
		db.session.commit()
		return load

	def setStatus(self, status):
		if status == "Completed" or status == "Invoiced":
			self.status = status

		numLocations = self.lane.locations.count()

		if numLocations < 2:
			status = "Missing Origin/Destination"
		#if (not self.created_by.company.is_carrier()) and len(filter((lambda bid: bid.accepted), self.bids)) < 1:
		#	status = "Pending Carrier Assignment"
		#if (not self.created_by.company.is_carrier()) and len(filter((lambda bid: bid.accepted), self.bids)) == 1:
		#	status = "Carrier Assigned"
		elif self.truck is None:
			status = "Waiting For Truck Assignment"
		else:
			status = "Truck Assigned"
			indx = 0
			for location in self.lane.locations:
				if indx == 0 and location.status_history.count() > 0:
					if (location.status_history[-1].status == "N/a" or
						location.status_history[-1].status == "En Route"):
						status = "En Route"
					if (location.status_history[-1].status == "Arrived" or
						location.status_history[-1].status == "Loaded/Unloaded"):
						status = "At Origin"
					elif location.status_history[-1].status == "Departed":
						status = "In Transit"
				elif indx == numLocations - 1 and location.status_history.count() > 0:
					if location.status_history[-1].status == "Arrived":
						status = "At Destination"
					elif (location.status_history[-1].status == "Departed" or
							location.status_history[-1].status == "Loaded/Unloaded"):
						status = "Delivered"
				indx += 1

		self.status = status

	#def getStatus(self):
	#	if self.status == "Completed" or self.status == "Invoiced":
	#		return self.status
#
#		numLocations = self.lane.locations.count()
#
#		if numLocations < 2:
#			status = "Missing Origin/Destination"
#		elif self.truck is None:
#			status = "Unnassigned"
#		else:
#			status = "Assigned"
#			indx = 0
#			for location in self.lane.locations:
#				if indx == 0 and location.status_history.count() > 0:
#					if (location.status_history[-1].status == "N/a" or
#						location.status_history[-1].status == "En Route"):
#						status = "En Route"
#					if (location.status_history[-1].status == "Arrived" or
#						location.status_history[-1].status == "Loaded/Unloaded"):
#						status = "At Origin"
#					elif location.status_history[-1].status == "Departed":
#						status = "In Transit"
#				elif indx == numLocations - 1 and location.status_history.count() > 0:
#					if location.status_history[-1].status == "Arrived":
#						status = "At Destination"
#					elif (location.status_history[-1].status == "Departed" or
#							location.status_history[-1].status == "Loaded/Unloaded"):
#						status = "Delivered"
#				indx += 1
#
#		self.status = status
#		return self.status


class Lane(db.Model):
	__tablename__ = 'Lane'
	id = db.Column(db.Integer, primary_key=True)
	load_id = db.Column(Integer, ForeignKey('Load.id'))
	locations = db.relationship('Location', backref='lane', lazy='dynamic')

	def __init__(self, locations):
		self.locations = locations

	@staticmethod
	def createLaneFromLocationArray(locations):
		lane = Lane(locations)
		db.session.add(lane)
		db.session.commit()
		return lane


class Location(db.Model):
	__tablename__ = 'Location'
	id = db.Column(db.Integer, primary_key=True)
	lane_id = db.Column(db.Integer, db.ForeignKey('Lane.id'))

	status_history = db.relationship('LocationStatus', backref='location', lazy='dynamic')
	
	address = db.relationship('Address', uselist=False, backref='location')

	notes = db.Column(db.String(1333))

	stop_type = db.Column(db.String(20))

	contact_id = db.Column(db.Integer, db.ForeignKey('Contact.id'))
	contact = relationship("Contact")

	stop_number = db.Column(db.Integer)
	arrival_date = db.Column(db.Date)

	type = db.Column(db.String(10))

	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))

	BOLs = relationship("BOL",
                    secondary=location_to_BOL)

	def __init__(self, address, arrival_date, stop_number, contact, stop_type, notes):
		self.address = address
		self.arrival_date = arrival_date
		self.stop_number = stop_number
		self.contact = contact
		self.stop_type = stop_type
		self.notes = notes
		url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
				'address': address
			}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

		response = urllib2.urlopen(url)
		data = response.read()
		try: 
			js = json.loads(str(data))
		except: js = None
		if 'status' not in js or js['status'] != 'OK':
			app.logger.error("Failed to Retrieve")

		latitude = None
		longitude = None
		if len(js["results"]) > 0:
			latitude = js["results"][0]["geometry"]["location"]["lat"]
			longitude = js["results"][0]["geometry"]["location"]["lng"]

		self.latitude = latitude
		self.longitude = longitude

	@staticmethod
	def createLocationFromForm(form):
		address = Address.createAddressFromForm(form)
		contact = Contact.createContactFromForm(form)
		

		stop_off = Location(address, form.arrival_date.data, form.stop_number.data, contact, form.stop_type.data, form.notes.data)
		
		

		db.session.add(stop_off)
		db.session.commit()
		return stop_off

	@staticmethod
	def findMatchingBOLByNumber(pickup_locations, form):
		for loc in pickup_locations:
			for this_BOL in loc.BOLs:
				if this_BOL.number == form.bol_number.data:
					return this_BOL

	def __repr__(self):
		return '%s, %s' % (self.address.city, self.address.state)

	def applyGeolocation(self):
		url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
				'address': address
			}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

		response = urllib2.urlopen(url)
		data = response.read()
		try: 
			js = json.loads(str(data))
		except: js = None
		if 'status' not in js or js['status'] != 'OK':
			app.logger.error("Failed to Retrieve")

		latitude = None
		longitude = None
		if len(js["results"]) > 0:
			latitude = js["results"][0]["geometry"]["location"]["lat"]
			longitude = js["results"][0]["geometry"]["location"]["lng"]

		self.latitude = latitude
		self.longitude = longitude

class LocationStatus(db.Model):
	__tablename__ = 'LocationStatus'
	id = db.Column(db.Integer, primary_key=True)
	location_id = db.Column(db.Integer, db.ForeignKey('Location.id'))
	status = db.Column(db.String(20))
	created_on = db.Column(db.DateTime, server_default=db.func.now())

	def __repr__(self):
		return '%s' % (self.status)

class LoadDetail(db.Model):
	__tablename__ = 'LoadDetail'
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(10))
	weight = db.Column(db.String(10))
	dim_length = db.Column(db.String(10))
	dim_width = db.Column(db.String(10))
	dim_height = db.Column(db.String(10))
	approx_miles = db.Column(db.String(10))
	number_pieces = db.Column(db.String(10))
	notes = db.Column(db.String(500))
	BOLs = relationship("BOL",
                    secondary=detail_to_BOL)



class Contact(db.Model):
	__tablename__ = 'Contact'
	id = db.Column(db.Integer, primary_key=True)
	contact_type = db.Column(db.String(20))
	name = db.Column(db.String(60))
	email = db.Column(db.String(30))
	phone = db.Column(db.String(30))

	brokered_loads = db.relationship('Load', backref='broker', lazy='dynamic', foreign_keys='Load.broker_id')
	shipped_loads = db.relationship('Load', backref='shipper', lazy='dynamic', foreign_keys='Load.shipper_id')
	__mapper_args__ = {'polymorphic_on': contact_type}

	@staticmethod
	def createContactFromForm(form):
		contact = Contact(name=form.contact_name.data,
					phone=form.contact_phone.data,
					email=form.contact_email.data)
		db.session.add(contact)
		db.session.commit()
		return contact

	def __repr__(self):
		return '%s' % (self.name)
	


class Fleet(db.Model):
	__tablename__ = 'Fleet'
	id = db.Column(db.Integer, primary_key=True)
	company_id = db.Column(db.Integer, db.ForeignKey('Company.id'))
	trucks = db.relationship('Truck', backref='Fleet', lazy='dynamic')
	drivers = db.relationship('Driver', backref='Fleet', lazy='dynamic')

	def __init__(self):
		self.trucks = []
		self.drivers = []


class Truck(db.Model):
	__tablename__ = 'Truck'
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	fleet_id = db.Column(db.Integer, ForeignKey('Fleet.id'))
	name = db.Column(db.String(100))
	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))
	is_available = db.Column(db.Boolean)
	trailer_group = db.Column(db.String(30))
	trailer_type = db.Column(db.String(30))
	max_weight = db.Column(db.String(10))
	dim_length = db.Column(db.String(10))
	dim_height = db.Column(db.String(10))
	dim_width = db.Column(db.String(10))
	tracker = db.relationship("LongLat", lazy='dynamic')
	driver = db.relationship('Driver', uselist=False, backref='truck')

	@staticmethod
	def createTruckFromJSON(json):
		truck = Truck(name=request.json.get('truckName'), 
						trailer_type=request.json.get('truckType'),
						max_weight=request.json.get('truckMaxWeight'),
						is_available=True,
						tracker = [])
		return truck

class Driver(db.Model):
	__tablename__ = 'Driver'
	id = db.Column(db.Integer, primary_key = True)
	fleet_id = db.Column(db.Integer, ForeignKey('Fleet.id'))
	#user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	truck_id = db.Column(db.Integer, db.ForeignKey('Truck.id'))
	first_name = db.Column(db.String(30))
	last_name = db.Column(db.String(30))
	driver_type = db.Column(db.String(30))
	email = db.Column(db.String(255), nullable=True)
	phone = db.Column(db.String(14))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	driver_account = db.relationship("User", backref="driver_instances")
	

	def get_phone_number(self):
		return str(self.phone)

	def get_full_name(self):
		return self.first_name + ' ' + self.last_name

	@staticmethod
	def createDriverFromUserData(user):
		driver = Driver(first_name=user.first_name, 
							last_name=user.last_name,
							email=user.email,
							phone=user.phone,
							driver_account=user)
		return driver

class LongLat(db.Model):
	__tablename__ = 'LongLat'
	id = db.Column(db.Integer, primary_key = True)
	latitude = db.Column(db.Float(6))
	longitude = db.Column(db.Float(6))

	truck_id = db.Column(db.Integer, db.ForeignKey('Truck.id'))
	load_id = db.Column(db.Integer, db.ForeignKey('Load.id'))

class Bid(db.Model):
	__tablename__ = "Bid"
	id = db.Column(db.Integer, primary_key = True)
	accepted = db.Column(db.Boolean)
	value = db.Column(db.String(150))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	created_by = db.relationship("User", backref="bids")
	load_id = db.Column(db.Integer, db.ForeignKey('Load.id'))

class BOL(db.Model):
	__tablename__ = "BOL"
	id = db.Column(db.Integer, primary_key = True)
	number = db.Column(db.String(20))
	number_units = db.Column(db.Integer)
	weight = db.Column(db.String(7))
	commodity_type = db.Column(db.String(255))
	dim_length = db.Column(db.String(7))
	dim_length_type = db.Column(db.String(7))
	dim_width = db.Column(db.String(7))
	dim_width_type = db.Column(db.String(7))
	dim_height = db.Column(db.String(7))
	dim_height_type = db.Column(db.String(7))

	@staticmethod
	def createBOLFromForm(form):
		bol = BOL(number=form.bol_number.data,
					number_units=form.number_units.data,
					weight=form.weight.data,
					commodity_type=form.commodity_type.data,
					dim_length=form.dim_length.data,
					dim_length_type=form.dim_length_type.data,
					dim_width=form.dim_width.data,
					dim_width_type=form.dim_width_type.data,
					dim_height=form.dim_height.data,
					dim_height_type=form.dim_height_type.data)
		db.session.add(bol)
		db.session.commit()
		return bol

	def __repr__(self):
		return self.number

class Token(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	#client_id = db.Column(db.String(40), db.ForeignKey('Client.client_id'), nullable=False)
	#client = db.relationship('Client')

	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	user = db.relationship('User')

	# currently only bearer is supported
	token_type = db.Column(db.String(40))

	access_token = db.Column(db.String(255), unique=True)
	refresh_token = db.Column(db.String(255), unique=True)
	expires = db.Column(db.DateTime)
	_scopes = db.Column(db.Text)

	def delete(self):
		db.session.delete(self)
		db.session.commit()
		return self

	@property
	def scopes(self):
		if self._scopes:
			return self._scopes.split()
		return []

