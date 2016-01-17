from flask import flash, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db
from app.models import User

def loginUser(user):
	user.authenticated = True
	db.session.add(user)
	db.session.commit()
	login_user(user, remember=False)
	# Tell Flask-Principal the user has logged in
	identity_changed.send(current_app._get_current_object(),
							identity=Identity(user.email))

def handleLoginFromForm(form):
	user = User.getUserByEmail(form.email.data)
	if user is not None:
		if not user.is_confirmed():
			flash("You must confirm your e-mail prior to logging in. To confirm your e-mail, click the activation link provided to %s" % user.email )

		if user.check_password(form.password.data) and not user.disabled:
			loginUser(user)
		elif user.disabled:
			flash("Your account has been disabled. Please contact your organization for more information.")
		else:
			flash("Wrong username/password")
	else:
		flash("Wrong username/password")

def handleLoginFromJSON(json):
	user = User.getUserByEmail(json.get('email'))
	if user is not None:
		if not user.is_confirmed():
			flash("You must confirm your e-mail prior to logging in. To confirm your e-mail, click the activation link provided to %s" % user.email )

		if user.check_password(json.get('password')) and not user.disabled:
			loginUser(user)
		elif user.disabled:
			flash("Your account has been disabled. Please contact your organization for more information.")
		else:
			flash("Wrong username/password")
	else:
		flash("Wrong username/password")

def handleLogout(user):
	user.authenticated = False
	db.session.add(user)
	db.session.commit()
	logout_user()

	#Remove session keys set by Flask-Principal
	for key in ('identity.name', 'identity.auth_type'):
		session.pop(key, None)

	# Tell Flask-Principal the user is anonymous
	identity_changed.send(current_app._get_current_object(),
							identity=AnonymousIdentity())