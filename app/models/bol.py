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
		return bol

	def __repr__(self):
		return self.number