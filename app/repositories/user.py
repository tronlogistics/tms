from app import app
from app import db
from app.models.user import User

class UserDI():

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
		user = User(first_name=json.get('firstName'),
				last_name=json.get('lastName'),
				phone=json.get('phoneNumber'),
				email=json.get('email'),
				password=json.get('password'))
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
