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

from app.models.associationtables import detail_to_BOL


class LoadDetail(db.Model):
	__tablename__ = 'LoadDetail'
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.String(10))
	weight = db.Column(db.String(10))
	dim_length = db.Column(db.String(10))
	dim_width = db.Column(db.String(10))
	dim_height = db.Column(db.String(10))
	approx_miles = db.Column(db.String(10))
	number_pieces = db.Column(db.String(10))
	notes = db.Column(db.String(500))
	BOLs = relationship("BOL",
                    secondary=detail_to_BOL)