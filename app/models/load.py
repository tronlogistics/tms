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


