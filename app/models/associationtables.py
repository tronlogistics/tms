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

Company_to_Load = db.Table('company_to_load', db.metadata,
	db.Column('company_id', db.Integer, db.ForeignKey('Company.id'), primary_key=True),
	db.Column('load_id', db.Integer, db.ForeignKey('Load.id'), primary_key=True)
)

User_to_Role = db.Table('user_to_role', db.metadata,
	db.Column('user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
	db.Column('role_id', db.Integer, db.ForeignKey('Role.id'), primary_key=True)
)

User_to_User = db.Table('user_to_user', db.metadata,
	db.Column('left_user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True),
	db.Column('right_user_id', db.Integer, db.ForeignKey('User.id'), primary_key=True)
)

detail_to_BOL = Table('detail_to_BOL', db.metadata,
    Column('detail_id', db.Integer, ForeignKey('LoadDetail.id')),
    Column('BOL_id', db.Integer, db.ForeignKey('BOL.id'))
)

location_to_BOL = Table('location_to_BOL', db.metadata,
    db.Column('location_id', db.Integer, ForeignKey('Location.id')),
    db.Column('BOL_id', db.Integer, db.ForeignKey('BOL.id'))
)

#assigned_Users = db.Table('assigned_Users', db.metadata,
#	Column('User_id', Integer, ForeignKey('User.id')),
#	Column('load_id', Integer, ForeignKey('Load.id'))
#)

assigned_Contacts = db.Table('assigned_Contacts', db.metadata,
	Column('Contact_id', Integer, ForeignKey('Contact.id')),
	Column('load_id', Integer, ForeignKey('Load.id'))
)