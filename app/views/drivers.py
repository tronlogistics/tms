from flask import Blueprint, render_template, url_for, redirect, request, flash, session, abort, g
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app
from app.forms import DriverForm, TruckForm, AssignDriverForm
from app.models import Load, Driver, Truck
from app.permissions import *

drivers = Blueprint('drivers', __name__, url_prefix='/drivers')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@drivers.before_request
def before_request():
	g.user = current_user


@drivers.route('/all', methods=['GET', 'POST'])
@drivers.route('/', methods=['GET', 'POST'])
@login_required
def all():
	return render_template('carrier/driver/all.html', 
							drivers=g.user.fleet.drivers, 
							title="All Drivers",
							active="Drivers",
							user=g.user)

@drivers.route('/assign', methods=['GET', 'POST'])
@login_required
def assign():
	form = AssignDriverForm()
	categories = [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]
	form.driver.choices = categories
	if form.validate_on_submit():
		truck = Truck.query.get(int(form.truck.data))
		driver = Driver.query.get(int(form.driver.data))
		driver.truck = truck
		form.driver.data = ('0', '<none selected>')
		db.session.add(driver)
		db.session.add(truck)
		db.session.commit()
	return redirect(url_for('carrier.all'))

@drivers.route('/remove/<driver_id>', methods=['GET', 'POST'])
@login_required
def remove(driver_id):
	driver = Driver.query.get(int(driver_id))
	driver.truck = None
	db.session.add(driver)
	db.session.commit()
	return redirect(url_for('carrier.all'))

#############################
#							#
#							#
#	   DRIVER - CRUD		#
#							#
#							#
#############################

@drivers.route('/create', methods=['GET', 'POST'])
@login_required
def create():
	if g.user.is_carrier():
		form = DriverForm()
		if form.validate_on_submit():
			driver = Driver(first_name=form.first_name.data, 
						last_name=form.last_name.data,
						email=form.email.data,
						phone=form.phone_number.data)

			db.session.add(driver)
			g.user.fleet.drivers.append(driver)
			db.session.add(g.user)
			db.session.commit()
			return redirect(url_for('.all'))
		return render_template('carrier/driver/create.html',
    							title="Create Driver",
    							form=form,
    							active="Drivers",
    							user=g.user)
	abort(403)

@drivers.route('/edit/<driver_id>', methods=['GET', 'POST'])
@login_required
def edit(driver_id):
	permission = EditDriverPermission(driver_id)
	if permission.can():
		form = DriverForm()
		driver = Driver.query.get(int(driver_id))
		if form.validate_on_submit():
			driver.first_name = form.first_name.data
			driver.last_name = form.last_name.data
			driver.email = form.email.data
			driver.phone = form.phone_number.data

			db.session.add(driver)
			db.session.commit()
			return redirect(url_for('.all'))
		else:
			form.first_name.data = driver.first_name 
			form.last_name.data = driver.last_name
			form.email.data = driver.email
			form.phone_number.data = driver.phone
			#form.phone_area_code.data = driver.phone_area_code
			#form.phone_prefix.data = driver.phone_prefix 
			#form.phone_line_number.data = driver.phone_line_number
		return render_template('carrier/driver/edit.html', 
								title="Edit Driver", 
								form=form, 
								driver=driver, 
								active="Drivers",
								user=g.user,
								edit=True)
	abort(403)

@drivers.route('/view/<driver_id>', methods=['GET', 'POST'])
@login_required
def view(driver_id):
	permission = ViewDriverPermission(driver_id)
	if permission.can():
		driver = Driver.query.get(int(driver_id))
		return render_template('carrier/driver/view.html', 
								title="View Driver", 
								driver=driver,
								active="Drivers", 
								user=g.user)
	abort(403)



@drivers.route('/delete/<driver_id>', methods=['GET', 'POST'])
@login_required
def delete(driver_id):
	permission = DeleteTruckPermission(driver_id)
	if permission.can():
		driver = Driver.query.get(int(driver_id))
		db.session.delete(driver)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)

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
	app.logger.info(error)
	db.session.rollback()
	return render_template('static/500.html'), 500

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
		for load in current_user.loads:
			identity.provides.add(EditLoadNeed(unicode(load.id)))
			identity.provides.add(DeleteLoadNeed(unicode(load.id)))
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			identity.provides.add(AssignLoadNeed(unicode(load.id)))
			identity.provides.add(InvoiceLoadNeed(unicode(load.id)))
			identity.provides.add(CompleteLoadNeed(unicode(load.id)))
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

		for driver in current_user.fleet.drivers:
			identity.provides.add(EditDriverNeed(unicode(driver.id)))
			identity.provides.add(DeleteDriverNeed(unicode(driver.id)))
			identity.provides.add(ViewDriverNeed(unicode(driver.id)))

	if hasattr(current_user, 'offered_bids'):
		for bid in current_user.offered_bids:
			identity.provides.add(ViewLoadNeed(unicode(bid.load.id)))
			identity.provides.add(AssignLoadNeed(unicode(bid.load.id)))
