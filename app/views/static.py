from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, mail
from app.forms import LoginForm, RegisterForm, ForgotForm, ResetPasswordForm, ContactUsForm, EmailForm, DemoForm
from app.models import User, Role, Lead
from app.permissions import *
from app.emails import register_account, new_lead, contact_us, reset_pass, get_serializer, request_demo
#from app import stripe, stripe_keys

static = Blueprint('static', __name__, url_prefix='')

@static.route('/', methods=['GET', 'POST'])
@static.route('/index', methods=['GET', 'POST'])
@static.route('/home', methods=['GET', 'POST'])
def index():
	return render_template('static/index.html')

@static.route('/features')
def features():
	return render_template('static/features.html')

@static.route('/demo', methods=['GET', 'POST'])
def demo():
	form = DemoForm()
	success = 0
	error = 0
	if form.validate_on_submit():
		request_demo(form)
		success = 1
	elif len(form.errors) > 0:
		flash(form.errors)
		error = 1
	return render_template('static/request_demo.html', form=form, success=success, error=error)

@static.route('/contact', methods=['GET', 'POST'])
def contact():
	form = ContactUsForm()
	success = 0
	contact_error = 0
	signup_error = 0
	#form.validate_on_submit()
	#flash(form.is_submitted())
	#flash(len(form.errors) > 0)

	if form.validate_on_submit():
		contact_us(form)
		success = 1
	elif len(form.errors) > 0:
		contact_error = 1
	
	return render_template('static/contact.html', form=form, success=success, 
		contact_error=contact_error,
		signup_error=signup_error)

@app.errorhandler(401)
def not_found_error(error):
	flash("You must sign in to view this page")
	return redirect(url_for('auth.login'))

@app.errorhandler(404)
def not_found_error(error):
	app.logger.exception(error)
	return render_template('static/404.html', user=current_user), 404

@app.errorhandler(500)
def internal_error(error):
	app.logger.exception(error)
	db.session.rollback()
	return render_template('static/500.html', user=current_user, error=error), 500

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
	# Set the identity user object
	identity.user = current_user

	# Add the UserNeed to the identity
	if hasattr(current_user, 'id'):
		identity.provides.add(UserNeed(current_user.id))

	# Assuming the User model has a list of roles, update the
	# identity with the roles that the user provides
	if hasattr(current_user, 'roles'):
		for role in current_user.roles:
			identity.provides.add(RoleNeed(role.name))

	# Assuming the User model has a list of posts the user
	# has authored, add the needs to the identity
	if hasattr(current_user, 'loads'):
		for load in current_user.loads:
			identity.provides.add(EditLoadNeed(unicode(load.id)))
			identity.provides.add(DeleteLoadNeed(unicode(load.id)))
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			identity.provides.add(AssignLoadNeed(unicode(load.id)))
			if load.truck is not None:
				identity.provides.add(ViewDriverNeed(unicode(load.truck.id)))
				if load.truck.driver is not None:
					identity.provides.add(ViewDriverNeed(unicode(load.truck.driver.id)))

	if hasattr(current_user, 'assigned_loads'):
		for load in current_user.assigned_loads:
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			identity.provides.add(AssignLoadNeed(unicode(load.id)))

	if hasattr(current_user, 'fleet'):
		for truck in current_user.fleet.trucks:
			identity.provides.add(EditTruckNeed(unicode(truck.id)))
			identity.provides.add(DeleteTruckNeed(unicode(truck.id)))
			identity.provides.add(ViewTruckNeed(unicode(truck.id)))
			identity.provides.add(RouteTruckNeed(unicode(truck.id)))

		for driver in current_user.fleet.drivers:
			identity.provides.add(EditDriverNeed(unicode(driver.id)))
			identity.provides.add(DeleteDriverNeed(unicode(driver.id)))
			identity.provides.add(ViewDriverNeed(unicode(driver.id)))

	if hasattr(current_user, 'offered_bids'):
		for bid in current_user.offered_bids:
			identity.provides.add(ViewLoadNeed(unicode(bid.load.id)))
			identity.provides.add(AssignLoadNeed(unicode(bid.load.id)))



