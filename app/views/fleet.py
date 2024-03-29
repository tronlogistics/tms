from flask import Blueprint, render_template, url_for, redirect, request, flash, session, abort, g
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app
from app.forms import DriverForm, TruckForm, AssignDriverForm
#from app.models import Load, Driver, Truck
from app.models.load import Load
from app.models.driver import Driver
from app.models.truck import Truck
from app.permissions import *

fleet = Blueprint('fleet', __name__, url_prefix='/fleet')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@fleet.before_request
def before_request():
	g.user = current_user


@fleet.route('/all', methods=['GET', 'POST'])
@fleet.route('/', methods=['GET', 'POST'])
@login_required
def view():
	if len(g.user.company.loads) == 0:
		unnasigned=0
		at_origin=0
		in_transit=0
		at_destination=0
		delivered=0
		invoiced=0
	else:
		unnasigned=len(filter((lambda load: load.status == "Unnasigned"), g.user.company.loads))
		at_origin=len(filter((lambda load: load.status == "At Origin"), g.user.company.loads))
		in_transit=len(filter((lambda load: load.status == "In Transit"), g.user.company.loads))
		at_destination=len(filter((lambda load: load.status == "At Destination"), g.user.company.loads))
		delivered=len(filter((lambda load: load.status == "Delivered"), g.user.company.loads))
		invoiced=len(filter((lambda load: load.status == "Invoiced"), g.user.company.loads))
	return render_template('carrier/all.html', 
							fleet=g.user.company.fleet, 
							title="View Fleet",
							active="Fleet",
							unnasigned=unnasigned,
							at_origin=at_origin,
							in_transit=in_transit,
							at_destination=at_destination,
							delivered=delivered,
							invoiced=invoiced,
							loads=g.user.company.loads,
							user=g.user)

@fleet.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
	form = AssignDriverForm()
	categories = [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.company.fleet.drivers)]
	form.driver.choices = categories
	if form.validate_on_submit():
		truck = Truck.query.get(int(form.truck.data))
		driver = Driver.query.get(int(form.driver.data))
		driver.truck = truck
		form.driver.data = ('0', '<none selected>')
		db.session.add(driver)
		db.session.add(truck)
		db.session.commit()
	return redirect(url_for('fleet.view'))

@fleet.route('/remove/<driver_id>', methods=['GET', 'POST'])
@login_required
def remove(driver_id):
	driver = Driver.query.get(int(driver_id))
	driver.truck = None
	db.session.add(driver)
	db.session.commit()
	return redirect(url_for('fleet.view'))


####################################



####################################

@app.errorhandler(401)
def not_found_error(error):
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
	print error
	app.logger.info(error)
	db.session.rollback()
	return render_template('static/500.html', error=error), 500

@identity_changed.connect
def on_identity_changed(sender, identity):
	# Set the identity user object
	identity.user = g.user
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
		for load in current_user.company.loads:
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			if len(filter((lambda user: user.id == load.created_by.id), g.user.company.users)) > 0:
				identity.provides.add(EditLoadNeed(unicode(load.id)))
				identity.provides.add(DeleteLoadNeed(unicode(load.id)))
			if g.user.company.is_carrier():
				identity.provides.add(AssignLoadNeed(unicode(load.id)))
				identity.provides.add(InvoiceLoadNeed(unicode(load.id)))
				identity.provides.add(CompleteLoadNeed(unicode(load.id)))
			if load.truck is not None:
				identity.provides.add(ViewTruckNeed(unicode(load.truck.id)))
				if load.truck.driver is not None:
					identity.provides.add(ViewDriverNeed(unicode(load.truck.driver.id)))

	#if hasattr(current_user, 'assigned_loads'):
	#	for load in current_user.assigned_loads:
	#		identity.provides.add(ViewLoadNeed(unicode(load.id)))
	#		identity.provides.add(AssignLoadNeed(unicode(load.id)))

	if hasattr(current_user, 'fleet'):
		for truck in current_user.compnay.fleet.trucks:
			identity.provides.add(EditTruckNeed(unicode(truck.id)))
			identity.provides.add(DeleteTruckNeed(unicode(truck.id)))
			identity.provides.add(ViewTruckNeed(unicode(truck.id)))

		for driver in current_user.compnay.fleet.drivers:
			identity.provides.add(EditDriverNeed(unicode(driver.id)))
			identity.provides.add(DeleteDriverNeed(unicode(driver.id)))
			identity.provides.add(ViewDriverNeed(unicode(driver.id)))

	if hasattr(current_user, 'offered_bids'):
		for bid in current_user.offered_bids:
			identity.provides.add(ViewLoadNeed(unicode(bid.load.id)))
			identity.provides.add(AssignLoadNeed(unicode(bid.load.id)))
