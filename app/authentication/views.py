from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app, jsonify, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, mail, authAPI, cors
from app.forms import LoginForm, RegisterForm, ForgotForm, ResetPasswordForm, ContactUsForm, EmailForm, DemoForm
from app.models import User, Role, Lead, Address, Company, Truck, Driver
from app.permissions import *
from app.emails import register_account, new_lead, contact_us, reset_pass, get_serializer, request_demo
from flask.ext.cors import CORS, cross_origin
from .registration.controller import registerUserFromForm, registerUserFromJSON
from .authentication.controller import handleLoginFromForm
#from app import stripe, stripe_keys

auth = Blueprint('auth', __name__, url_prefix='/u')

@lm.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@auth.before_request
def before_request():
    g.user = current_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
	if g.user.is_authenticated():
		return redirect(url_for('fleet.view'))
	
	login_form = LoginForm()
	
	if login_form.validate_on_submit():
		handleLoginFromForm(login_form)
		if g.user.is_authenticated():
			return redirect(url_for('fleet.view'))

	return render_template('auth/login.html', login_form=login_form, register_form=RegisterForm(), forgot_form=ForgotForm(), user=g.user)

@auth.route("/logout", methods=["GET"])
@login_required
def logout():
    #Logout the current user.
    handleLogout(g.user)

    return redirect(url_for('.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
	register_form = RegisterForm()
	if register_form.validate_on_submit():
		registerUserFromForm(register_form)
	return redirect(url_for('.login', type='register'))

@auth.route('/activate/<activation_slug>')
def activate_user(activation_slug):
    user = User.getUserByActivationSlug(activation_slug)
    activateUser(user)
    
    if user.password == "":
    	return redirect(url_for('.set_password', user_id=user_id))
    else:
    	flash('Your account is now activated. Please log in.')
    	return redirect(url_for('.login'))

@auth.route('/reset/<activation_slug>', methods=['GET', 'POST'])
def reset_password(activation_slug):
	form = ResetPasswordForm()

	if form.validate_on_submit():
		handlePasswordReset(g.user, form)
		return redirect(url_for('fleet.view'))
	else:
		user = User.getUserByActivationSlug(activation_slug)
		login_user(user, remember=False)
		app.logger.info("User \"%s\"'s password is now reset" % user.email)
		flash('Your password has been reset. Please create a new password.')

		return render_template('auth/reset_password.html', form=form, user=user)

@auth.route('/<user_id>/set_password', methods=['GET', 'POST'])
def set_password(user_id):
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.getUserByID(user_id)
		setPasswordForUser(user, form)
		flash("Your password has been set.")
		if len(user.roles) == 1 and user.roles[0].code == 'driver':
			return redirect(url_for('trucks.check_in'))
		else:
			return redirect(url_for('fleet.view'))
	else:
		return render_template('auth/create_password.html', form=form, user_id=user_id)

#### API ####

@auth.route('/api/users', methods=['POST'])
def new_user():
	email = request.json.get('email')
	password = request.json.get('password')
	if email is None or password is None:
		abort(400)    # missing arguments
	if User.query.filter_by(email=email).first() is not None:
		abort(400)    # existing user
	registerUserFromJSON(request.json)
	
	token = User.getUserByEmail(email).generate_auth_token()
	return (jsonify({ 'token': token.decode('ascii') }), 201)

@auth.route('/api/login', methods=['POST'])
def api_login_user():
	email = request.json.get('email')
	password = request.json.get('password')
	if email is None or password is None:
		abort(400)    # missing arguments
	user = User.getUserByEmail(email)
	if not user.isOwnerOperator():
		return abort(403)
	if user is None:
		abort(400)    # no existing user
	if user.check_password(password):
		loginUser(user)
		g.user = user
		token = g.user.generate_auth_token()
		return (jsonify({
						'token': token.decode('ascii'), 
						'isOwnerOperator': len(filter(lambda role: role.code == "owner_operator", user.roles)) > 0 
						}))
	else:
		return abort(401)


#############


@app.errorhandler(401)
def no_access_error(error):
	flash("You must sign in to view this page")
	return redirect(url_for('auth.login'))

@app.errorhandler(403)
def forbidden_error(error):
	app.logger.info(error)
	return render_template('static/404.html'), 403

@app.errorhandler(404)
def not_found_error(error):
	app.logger.info(error)
	return render_template('static/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	print "%s" % error
	app.logger.info(error)
	db.session.rollback()
	return render_template('static/500.html', error=error), 500
