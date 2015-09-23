from flask import Blueprint, render_template, url_for, redirect, request, flash, session, abort, g, jsonify
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, mail
from app.forms import DriverForm, TruckForm, AssignDriverForm, LocationStatusForm, RouteForm, AssignDriverForm
from app.models import Load, Driver, Truck, LongLat, Location, LocationStatus
from app.permissions import *
from app.emails import ping_driver, get_serializer
from itsdangerous import URLSafeSerializer, BadSignature
from datetime import datetime

trucks = Blueprint('trucks', __name__, url_prefix='/trucks')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@trucks.before_request
def before_request():
	g.user = current_user


#############################
#							#
#							#
#	   TRUCK - CRUD			#
#							#
#							#
#############################

@trucks.route('/all', methods=['GET', 'POST'])
@login_required
def all():
	return render_template("carrier/truck/all.html", 
							trucks=g.user.company.fleet.trucks, 
							user=g.user,
							active="Trucks",
							title="All Trucks")

@trucks.route('/create', methods=['GET', 'POST'])
@login_required
def create():
	if g.user.company.is_carrier():
		form = TruckForm()
		if form.validate_on_submit():
			truck = Truck(name=form.name.data, 
						trailer_type=form.trailer_type.data,
						max_weight=form.max_weight.data,
						dim_length=form.dim_length.data,
						dim_height=form.dim_height.data,
						dim_width=form.dim_width.data,
						is_available=True,
						tracker = [])
			db.session.add(truck)
			g.user.company.fleet.trucks.append(truck)
			db.session.add(g.user.company)
			db.session.commit()
			return redirect(url_for('.view', truck_id=truck.id))
		return render_template('carrier/truck/create.html',
    							title="Create Truck",
    							form=form,
    							active="Trucks",
    							user=g.user)
	abort(403)



@trucks.route('/edit/<truck_id>', methods=['GET', 'POST'])
@login_required
def edit(truck_id):
	permission = EditTruckPermission(truck_id)
	if permission.can():
		form = TruckForm()
		truck = Truck.query.get(int(truck_id))
		if form.validate_on_submit():
			truck.name = form.name.data
			for locationData in form.locations:
				app.logger.info("%s - %s" % (locationData.location_id.data, locationData.stop_number.data))
				location = Location.query.get(int(locationData.location_id.data))
				location.stop_number = int(locationData.stop_number.data)
				app.logger.info("%s - %s" % (location.address.postal_code, location.stop_number))
				db.session.add(location)
			#carrier.latitude = form.latitude.data
			#carrier.longitude = form.longitude.data
			db.session.add(truck)
			db.session.commit()
			return redirect(url_for('.all'))
		else:
			#form.latitude.data = carrier.latitude
			#form.longitude.data = carrier.longitude
			form.name.data = truck.name
			form.trailer_type.data = truck.trailer_type
			form.max_weight.data = truck.max_weight
			form.dim_length.data = truck.dim_length
			form.dim_height.data = truck.dim_height
			form.dim_width.data = truck.dim_width

		locations = []
		for load in truck.loads:
			for location in load.lane.locations:
				locations.append(location)

		return render_template('carrier/truck/edit.html', 
								title="Edit Truck", 
								locations=locations,
								form=form, 
								truck=truck, 
								active="Trucks",
								user=g.user,
								edit=True)
	abort(403)

@trucks.route('/view/<truck_id>', methods=['GET', 'POST'])
@login_required
def view(truck_id):
	permission = ViewTruckPermission(truck_id)
	if permission.can():
		form = LocationStatusForm()
		assign_form = AssignDriverForm()
		categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.company.fleet.drivers)]
		assign_form.driver.choices = categories
		truck = Truck.query.get_or_404(truck_id)
		location = getNextLocation(truck)
		if form.validate_on_submit():
			status = LocationStatus(status=form.status.data, created_on=datetime.utcnow())
			location.status_history.append(status)
			location.status = form.status.data
			db.session.add(status)
			db.session.add(location)
			
			if location.status == "Departed":
				changeStopNumbers(truck)
				location = getNextLocation(truck)
				#status = locationStatus(status="En Route", created_on=datetime.utcnow())
				#location.status_history.append(status)
				#location.staus = "En Route"
				#db.session.add(location)
				if location is None:
					flash("Truck is now idle. Assign a load to this truck")
				else:
					flash("A new location has been set for the truck")
			for load in truck.loads:
				load.setStatus(None)
				db.session.add(load)
			db.session.add(truck)
			db.session.commit()
		elif form.is_submitted():
			flash("There was an error updating the location status")


		#categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]# + [('-1', 'Create New Driver...')]
		#form.driver.choices = categories
		#truck = Truck.query.get(int(truck_id))
		locations = []
		for load in truck.loads:
			for load_location in filter((lambda load_location: load_location.stop_number > 0 ), 
												load.lane.locations):
				locations.append(load_location)
		return render_template('carrier/truck/view.html', 
								title="View Truck", 
								location=location,
								locations=locations,
								form=form, 
								assign_form=assign_form,
								truck=truck, 
								user=g.user)
	abort(403)


	



@trucks.route('/delete/<truck_id>', methods=['GET', 'POST'])
@login_required
def delete(truck_id):
	permission = DeleteTruckPermission(truck_id)
	if permission.can():
		truck = Truck.query.get(int(truck_id))
		db.session.delete(truck)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)

###########################################

@trucks.route('/ping/<truck_id>', methods=['GET', 'POST'])
def ping(truck_id):
	truck = Truck.query.get(int(truck_id))
	ping_driver(truck.driver)
	return jsonify({'message': 'Pinged ' + truck.driver.get_full_name()})

@trucks.route('/checkin/<activation_slug>', methods=['GET', 'POST'])
def check_in(activation_slug):
	form = LocationStatusForm()

	s = get_serializer()
	try:
		driver_id = s.loads(activation_slug)
		app.logger.info("Truck %s" % driver_id)
	except BadSignature:
		abort(404)

	truck = Driver.query.get_or_404(driver_id).truck
	location = getNextLocation(truck)
	if form.validate_on_submit():
		status = LocationStatus(status=form.status.data, created_on=datetime.utcnow())
		location.status_history.append(status)
		location.status = form.status.data
		if location.status == "Departed":
			changeStopNumbers(truck)
			location = getNextLocation(truck)
		db.session.add(location)
		db.session.commit()
	#if location.status_history.count > 0:
	#	form.status.data = location.status_history[-1].status
	return render_template('carrier/truck/checkin.html', truck=truck, location=location, form=form)

@trucks.route('/storelocation/<truck_id>', methods=['POST'])
def store_location(truck_id):
	try:
		truck = Truck.query.get(int(truck_id))
		longlat = LongLat(latitude=request.form['lat'],
							longitude=request.form['long'])
		truck.tracker.append(longlat)
		for load in filter((lambda l: l.status != "Load Complete"), truck.driver.loads):
			load.tracker.append(longlat)
		if truck.tracker.count() > 10: 
			db.session.delete(truck.tracker.first())
		db.session.add(truck)
		db.session.add(load)
		db.session.commit()
		return jsonify({'message': 'Thank you for checking in at %s, %s' % (longlat.latitude, longlat.longitude)})
	except Exception as e:
		return jsonify({'message': '%s' % e })

@trucks.route('/route/<truck_id>', methods=['GET', 'POST'])
@login_required
def route(truck_id):
	permission = RouteTruckPermission(truck_id)
	if permission.can():
		form = RouteForm()
		truck = Truck.query.get_or_404(truck_id)
		if form.validate_on_submit():
			for locationData in form.locations:
				location = Location.query.get(int(locationData.location_id.data))
				location.stop_number = int(locationData.stop_number.data)
				db.session.add(location)
			db.session.add(location)
			db.session.commit()
			return redirect(url_for('.view', truck_id=truck.id))

		#categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]# + [('-1', 'Create New Driver...')]
		#form.driver.choices = categories
		#truck = Truck.query.get(int(truck_id))
		locations = []
		for load in truck.loads:
			for load_location in filter((lambda load_location: load_location.stop_number > 0 ), 
												load.lane.locations):
				locations.append(load_location)
		return render_template('carrier/truck/route.html', 
								title="Route Truck", 
								locations=locations,
								form=form,

								active="Trucks",
								user=g.user,
								truck=truck,
								edit=True)
	abort(403)

@trucks.route('/view/<truck_id>/assign', methods=['GET', 'POST'])
@login_required
def assign(truck_id):
	form = AssignDriverForm()
	categories = [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.company.fleet.drivers)]
	form.driver.choices = categories
	truck = Truck.query.get(int(truck_id))
	if form.validate_on_submit():
		driver = Driver.query.get(int(form.driver.data))
		truck.driver = driver
		db.session.add(driver)
		db.session.add(truck)
		db.session.commit()
	else:
		flash("There was an error assigning that driver")
	return redirect(url_for('.view', truck_id=truck.id))

##########
#  MISC  #
##########

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
	print "%s" % error
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

###########################

def getNextLocation(truck):
	for load in truck.loads:
		for location in load.lane.locations:
			app.logger.info("%s, %s" % (location.stop_number, int(location.stop_number) == 1))

			if int(location.stop_number) == 1:
				app.logger.info("returning %s" % location.stop_number)
				return location
	return None

def getUpcomingLocations(truck):
	locations = []
	for load in filter(lambda cur: cur.status != "Completed", truck.driver.loads):
		for location in filter(lambda cur: cur.Status != "Departed", load.lane.locations):
			locations.append(location)
	return locations

def changeStopNumbers(truck):
	for load in truck.loads:
		for location in load.lane.locations:
			location.stop_number -= 1
			db.session.add(location)