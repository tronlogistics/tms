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