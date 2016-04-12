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

from app.models.associationtables import Company_to_Load
from app.models.fleet import Fleet

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

	
