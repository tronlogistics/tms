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


	def __repr__(self):
		if self.address1 is None or self.address1 == "":
			return self.city + ", " + self.state + " " + self.postal_code
		else:
			return self.address1 + ", " + self.city + ", " + self.state + " " + self.postal_code