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

from app.models.associationtables import location_to_BOL

class Location(db.Model):
	__tablename__ = 'Location'
	id = db.Column(db.Integer, primary_key=True)
	lane_id = db.Column(db.Integer, db.ForeignKey('Lane.id'))

	status_history = db.relationship('Status', backref='location', lazy='dynamic')
	
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