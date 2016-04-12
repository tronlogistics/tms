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

class Bid(db.Model):
	__tablename__ = "Bid"
	id = db.Column(db.Integer, primary_key = True)
	accepted = db.Column(db.Boolean)
	value = db.Column(db.String(150))
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	created_by = db.relationship("User", backref="bids")
	load_id = db.Column(db.Integer, db.ForeignKey('Load.id'))