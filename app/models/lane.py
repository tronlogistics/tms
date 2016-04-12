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

class Lane(db.Model):
	__tablename__ = 'Lane'
	id = db.Column(db.Integer, primary_key=True)
	load_id = db.Column(Integer, ForeignKey('Load.id'))
	locations = db.relationship('Location', backref='lane', lazy='dynamic')

	def __init__(self, locations):
		self.locations = locations

	