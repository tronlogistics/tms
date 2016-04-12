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

#TODO - Sublcass contact into various contact types (user contact, load contact, etc)
#TODO - Create a contact on user entity which stores the user info

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

	def __repr__(self):
		return '%s' % (self.name)