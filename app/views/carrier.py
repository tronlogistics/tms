from flask import Blueprint, render_template, url_for, redirect, request, flash, session, abort, g
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app
from app.forms import DriverForm, TruckForm, AssignDriverForm
from app.models import Load, Driver, Truck
from app.permissions import *

carrier = Blueprint('carrier', __name__, url_prefix='/fleet')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@carrier.before_request
def before_request():
	g.user = current_user


@carrier.route('/all', methods=['GET', 'POST'])
@carrier.route('/', methods=['GET', 'POST'])
@login_required
def all():
	form = AssignDriverForm()	
	categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]# + [('-1', 'Create New Driver...')]
	form.driver.choices = categories
	#if form.driver.data == -1:
	#		session['truck'] = int(form.truck.data)
	#		return redirect(url_for('carrier.create_driver'))

	if form.validate_on_submit():
		truck = Truck.query.get(int(form.truck.data))
		driver = Driver.query.get(int(form.driver.data))
		driver.truck = truck
		form.driver.data = ('0', '<none selected>')
		db.session.add(driver)
		db.session.add(truck)
		db.session.commit()

	categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]# + [('-1', 'Create New Driver...')]
	return render_template('carrier/all.html', fleet=g.user.fleet, form=form, user=g.user)

@carrier.route('/assign', methods=['GET', 'POST'])
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

@carrier.route('/remove/<driver_id>', methods=['GET', 'POST'])
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
#	   TRUCK - CRUD			#
#							#
#							#
#############################

@carrier.route('/trucks/create', methods=['GET', 'POST'])
@login_required
def create_truck():
	if g.user.is_carrier():
		form = TruckForm()
		if form.validate_on_submit():
			truck = Truck(name=form.name.data, 
						trailer_group=form.trailer_group.data,
						trailer_type=form.trailer_type.data,
						max_weight=form.max_weight.data,
						dim_length=form.dim_length.data,
						dim_height=form.dim_height.data,
						dim_width=form.dim_width.data,
						is_available=True)
			db.session.add(truck)
			g.user.fleet.trucks.append(truck)
			db.session.add(g.user)
			db.session.commit()
			return redirect(url_for('.all'))
		return render_template('carrier/truck/create.html',
    							title="Create Truck",
    							form=form,
    							user=g.user)
	abort(403)



@carrier.route('/trucks/edit/<truck_id>', methods=['GET', 'POST'])
@login_required
def edit_truck(truck_id):
	permission = EditTruckPermission(truck_id)
	if permission.can():
		form = TruckForm()
		truck = Truck.query.get(int(truck_id))
		if form.validate_on_submit():
			truck.name = form.name.data
			#carrier.latitude = form.latitude.data
			#carrier.longitude = form.longitude.data
			db.session.add(truck)
			db.session.commit()
			return redirect(url_for('.all'))
		else:
			#form.latitude.data = carrier.latitude
			#form.longitude.data = carrier.longitude
			form.name.data = truck.name
			form.trailer_group.data = truck.trailer_group
			form.trailer_type.data = truck.trailer_type
			form.max_weight.data = truck.max_weight
			form.dim_length.data = truck.dim_length
			form.dim_height.data = truck.dim_height
			form.dim_width.data = truck.dim_width
		return render_template('carrier/truck/edit.html', title="Edit Truck", form=form, truck=truck, user=g.user)
	abort(403)

@carrier.route('/trucks/view/<truck_id>', methods=['GET', 'POST'])
@login_required
def view_truck(truck_id):
	permission = ViewTruckPermission(truck_id)
	if permission.can():
		form = AssignDriverForm()
		categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]# + [('-1', 'Create New Driver...')]
		form.driver.choices = categories
		truck = Truck.query.get(int(truck_id))
		return render_template('carrier/truck/view.html', title="View Truck", form=form, truck=truck, user=g.user)
	abort(403)



@carrier.route('/trucks/delete/<truck_id>', methods=['GET', 'POST'])
@login_required
def delete_truck(truck_id):
	permission = DeleteTruckPermission(truck_id)
	if permission.can():
		truck = Truck.query.get(int(truck_id))
		db.session.delete(truck)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)

#############################
#							#
#							#
#	   DRIVER - CRUD		#
#							#
#							#
#############################

@carrier.route('/drivers/create', methods=['GET', 'POST'])
@login_required
def create_driver():
	if g.user.is_carrier():
		form = DriverForm()
		if form.validate_on_submit():
			driver = Driver(first_name=form.first_name.data, 
						last_name=form.last_name.data)

			driver.phone_area_code = str(form.phone_area_code.data)
			if len(driver.phone_area_code) < 3:
				prepend_value = ""
				for x in range(0, 3 - len(driver.phone_area_code)):
					prepend_value += "0"
				driver.phone_area_code = prepend_value + driver.phone_area_code
			
			driver.phone_prefix = str(form.phone_prefix.data)
			if len(driver.phone_prefix) < 3:
				prepend_value = ""
				for x in range(0, 3 - len(driver.phone_prefix)):
					prepend_value += "0"
				driver.phone_prefix = prepend_value + driver.phone_prefix
			
			driver.phone_line_number = str(form.phone_line_number.data)
			if len(driver.phone_line_number) < 4:
				prepend_value = ""
				for x in range(0, 4 - len(driver.phone_line_number)):
					prepend_value += "0"
				driver.phone_line_number = prepend_value + driver.phone_line_number

			db.session.add(driver)
			g.user.fleet.drivers.append(driver)
			db.session.add(g.user)
			db.session.commit()
			return redirect(url_for('.all'))
		return render_template('carrier/driver/create.html',
    							title="Create Driver",
    							form=form,
    							user=g.user)
	abort(403)

@carrier.route('/drivers/edit/<driver_id>', methods=['GET', 'POST'])
@login_required
def edit_driver(driver_id):
	permission = EditDriverPermission(driver_id)
	if permission.can():
		form = DriverForm()
		driver = Driver.query.get(int(driver_id))
		if form.validate_on_submit():
			driver.first_name = form.first_name.data
			driver.last_name = form.last_name.data

			driver.phone_area_code = str(form.phone_area_code.data)
			if len(driver.phone_area_code) < 3:
				prepend_value = ""
				for x in range(0, 3 - len(driver.phone_area_code)):
					prepend_value += "0"
				driver.phone_area_code = prepend_value + driver.phone_area_code
			
			driver.phone_prefix = str(form.phone_prefix.data)
			if len(driver.phone_prefix) < 3:
				prepend_value = ""
				for x in range(0, 3 - len(driver.phone_prefix)):
					prepend_value += "0"
				driver.phone_prefix = prepend_value + driver.phone_prefix
			
			driver.phone_line_number = str(form.phone_line_number.data)
			if len(driver.phone_line_number) < 4:
				prepend_value = ""
				for x in range(0, 4 - len(driver.phone_line_number)):
					prepend_value += "0"
				driver.phone_line_number = prepend_value + driver.phone_line_number

			db.session.add(driver)
			db.session.commit()
			return redirect(url_for('.all'))
		else:
			form.first_name.data = driver.first_name 
			form.last_name.data = driver.last_name
			form.phone_area_code.data = driver.phone_area_code
			form.phone_prefix.data = driver.phone_prefix 
			form.phone_line_number.data = driver.phone_line_number
		return render_template('carrier/driver/edit.html', title="Edit Driver", form=form, driver=driver, user=g.user)
	abort(403)

@carrier.route('/drivers/view/<driver_id>', methods=['GET', 'POST'])
@login_required
def view_driver(driver_id):
	permission = ViewDriverPermission(driver_id)
	if permission.can():
		driver = Driver.query.get(int(driver_id))
		return render_template('carrier/driver/view.html', title="View Driver", driver=driver, user=g.user)
	abort(403)



@carrier.route('/drivers/delete/<driver_id>', methods=['GET', 'POST'])
@login_required
def delete_driver(driver_id):
	permission = DeleteTruckPermission(driver_id)
	if permission.can():
		driver = Driver.query.get(int(driver_id))
		db.session.delete(driver)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)

####################################



####################################

@identity_changed.connect_via(app)
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
	if hasattr(current_user, 'brokered_loads'):
		for load in current_user.brokered_loads:
			identity.provides.add(EditLoadNeed(unicode(load.id)))
			identity.provides.add(DeleteLoadNeed(unicode(load.id)))
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			identity.provides.add(AssignLoadNeed(unicode(load.id)))

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
