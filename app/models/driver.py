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