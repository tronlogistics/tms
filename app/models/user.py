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

from app.models.associationtables import User_to_Role
from app.repositories.rolerepository import RoleDI
from app.emails import get_serializer

class User(db.Model):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key=True)

	#Foreign key to company
	company_id = db.Column(db.Integer, db.ForeignKey('Company.id'))

	# User authentication information
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)
	password = db.Column(db.String(255), nullable=False, server_default='')
	#reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

	
	confirmed_at = db.Column(db.DateTime())

	# User information
	authenticated = db.Column(db.Boolean(), nullable=False, server_default='0')
	first_name = db.Column(db.String(100), nullable=False, server_default='')
	last_name = db.Column(db.String(100), nullable=False, server_default='')
	phone = db.Column(db.String(30))

	#Is account disabled
	disabled = db.Column(db.Boolean)

	#User Roles
	roles = db.relationship("Role",
                    secondary=User_to_Role)

	#Stripe Customer Identier
	customer_id = db.Column(db.Integer)

	def __init__(self, email, first_name, last_name, phone, password):
		self.email = email.lower()
		self.first_name = first_name
		self.last_name = last_name
		self.phone = phone
		self.roles = []
		if password != "":
			self.set_password(password)

	def is_carrier(self):
		return len(filter((lambda role: role.name == 'carrier'), self.roles)) == 1

	def get_id(self):
		return self.id

	def is_active(self):
		#True, as all Users are active.
		return True

	def is_authenticated(self):
		#'Return True if the User is authenticated.'
		return self.authenticated

	def is_anonymous(self):
		#False, as anonymous Users aren't supported.'
		return False

	def set_password(self, password):
		self.password = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password, password)

	def hash_password(self, password):
		self.password = pwd_context.encrypt(password)

	def verify_password(self, password):
		return pwd_context.verify(password, self.password)

	def activate(self):
		self.confirmed_at = datetime.now()

	def is_confirmed(self):
		return self.confirmed_at is not None

	def is_company_admin(self):
		return len(filter((lambda role: role.code == 'company_admin'), self.roles)) > 0

	def is_admin(self):
		return len(filter((lambda role: role.code == 'admin'), self.roles)) > 0

	def isOwnerOperator(self):
		return len(filter(lambda role: role.code == "owner_operator", self.roles)) > 0

	def generate_auth_token(self, expiration=1892160000):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})

	def makeCompanyAdmin(self):
		role = RoleDI.findRoleByType('company_admin')
		self.roles.append(role)

	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None    # valid token, but expired
		except BadSignature:
			return None    # invalid token
		user = User.query.get(data['id'])
		return user

	@staticmethod
	def createUserFromForm(form):
		user = User(first_name=form.first_name.data,
				last_name=form.last_name.data,
				phone=form.phone_number.data,
				email=form.email.data,
				password=form.password.data)
		return user

	@staticmethod
	def createUserFromJSON(json):
		user = User(first_name=request.json.get('firstName'),
				last_name=request.json.get('lastName'),
				phone=request.json.get('phoneNumber'),
				email=request.json.get('email'),
				password=request.json.get('password'))
		return user

	@staticmethod
	def getUserByEmail(email):
		return User.query.filter_by(email=email.lower()).first()

	@staticmethod
	def getUserByID(email):
		return User.query.get_or_404(user_id)

	@staticmethod
	def getUserByActivationSlug(activation_slug):
		s = get_serializer()
		try:
			user_id = s.loads(activation_slug)
		except BadSignature:
			abort(404)

		user = User.query.get_or_404(user_id)
		return user

	def __repr__(self):
		return '%s %s' % (self.first_name, self.last_name)
