from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, abort
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, SQLAlchemy
from app.forms import LoadForm, StatusForm, LaneLocationForm, LocationStatusForm
from app.models import Load, LoadDetail, Lane, Location, Truck, User, Driver, Contact
from app.permissions import *
from app.controllers import LoadFactory, AddressFactory, LocationFactory, LoadDetailFactory, ContactFactory
#from app.factories
from sqlalchemy import desc


loads = Blueprint('loads', __name__, url_prefix='/loads')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@loads.before_request
def before_request():
	g.user = current_user

@loads.route('/create', methods=['GET', 'POST'])
@login_required
def create():
	form = LoadForm()
	if form.validate_on_submit():
		#geolocator = Nominatim()
		#load = Load(name=form.name.data, 
		#			price=form.price.data, 
		#			description=form.description.data) 
		#if g.user.is_carrier():
		#	load.status="Pending Truck Assignment"
		#	load.carrier=g.user
		#	load.carrier_cost=form.price.data
		#else:
		#	load.status="Unassigned"
		#load.assigned_driver = None
		#db.session.add(load)
		#g.user.brokered_loads.append(load)

		#for location in form.locations:
		#	app.logger.exception("Location: %s" % location.address1.data)			

		#origin = Location(address1=form.origin_address1.data,
		#					address2=form.origin_address2.data,
		#					city=form.origin_city.data,
		#					state=form.origin_state.data,
		#					postal_code=form.origin_postal_code.data,
		#					contact_name=form.origin_contact_name.data,
		#					contact_email=form.origin_contact_email.data)

		#origin.contact_phone_area_code = str(form.origin_contact_phone_area_code.data)
		#if len(origin.contact_phone_area_code) < 3:
		#	prepend_value = ""
		#	for x in range(0, 3 - len(origin.contact_phone_area_code)):
		#		prepend_value += "0"
		#	origin.contact_phone_area_code = prepend_value + origin.contact_phone_area_code
		
		#origin.contact_phone_prefix = str(form.origin_contact_phone_prefix.data)
		#if len(origin.contact_phone_prefix) < 3:
		#	prepend_value = ""
		#	for x in range(0, 3 - len(origin.contact_phone_prefix)):
		#		prepend_value += "0"
		#	origin.contact_phone_prefix = prepend_value + origin.contact_phone_prefix
		
		#origin.contact_phone_line_number = str(form.origin_contact_phone_line_number.data)
		#if len(origin.contact_phone_line_number) < 4:
		#	prepend_value = ""
		#	for x in range(0, 4 - len(origin.contact_phone_line_number)):
		#		prepend_value += "0"
		#	origin.contact_phone_line_number = prepend_value + origin.contact_phone_line_number

		#location = geolocator.geocode(origin.postal_code)
		#origin.latitude = location.latitude
		#origin.longitude = location.longitude
		#db.session.add(origin)
		#destination = Location(address1=form.destination_address1.data,
		#					address2=form.destination_address2.data,
		#					city=form.destination_city.data,
		#					state=form.destination_state.data,
		#					postal_code=form.destination_postal_code.data,
		#					contact_name=form.destination_contact_name.data,
		#					contact_email=form.destination_contact_email.data)

		#destination.contact_phone_area_code = str(form.destination_contact_phone_area_code.data)
		#if len(destination.contact_phone_area_code) < 3:
		#	prepend_value = ""
		#	for x in range(0, 3 - len(destination.contact_phone_area_code)):
		#		prepend_value += "0"
		#	destination.contact_phone_area_code = prepend_value + destination.contact_phone_area_code
		
		#destination.contact_phone_prefix = str(form.destination_contact_phone_prefix.data)
		#if len(destination.contact_phone_prefix) < 3:
		#	prepend_value = ""
		#	for x in range(0, 3 - len(destination.contact_phone_prefix)):
		#		prepend_value += "0"
		#	destination.contact_phone_prefix = prepend_value + destination.contact_phone_prefix
		
		#destination.contact_phone_line_number = str(form.destination_contact_phone_line_number.data)
		#if len(destination.contact_phone_line_number) < 4:
		#	prepend_value = ""
		#	for x in range(0, 4 - len(destination.contact_phone_line_number)):
		#		prepend_value += "0"
		#	destination.contact_phone_line_number = prepend_value + destination.contact_phone_line_number
		#location = geolocator.geocode(destination.postal_code)
		#destination.latitude = location.latitude
		#destination.longitude = location.longitude
		#db.session.add(destination)
		#lane = Lane(origin=origin, destination=destination)
		#db.session.add(lane)

		#load_detail = LoadDetail(weight = form.weight.data,
		#						dim_length = form.dim_length.data,
		#						dim_width = form.dim_width.data,
		#						dim_height = form.dim_height.data,
		#						number_pieces = form.number_pieces.data,
		#						comments = form.comments.data,
		#						pickup_date=form.pickup_date.data, 
		#						delivery_date=form.delivery_date.data,
		#						trailer_type=form.trailer_type.data,
		#						load_type=form.load_type.data,
		#						total_miles=form.total_miles.data,
		#						purchase_order = form.purchase_order.data,
		#						over_dimensional = form.over_dimensional.data)
		#db.session.add(load_detail)
		#load.lane = lane
		#load.load_detail = load_detail
		#load.broker = g.user
		load = LoadFactory(form)
		g.user.loads.append(load)
		if g.user.is_carrier:
			load.status="Pending Truck Assignment"
			load.carrier=g.user
			load.carrier_cost=form.price.data
		else:
			load.status="Unassigned"
		db.session.add(load)
		db.session.add(g.user)
		db.session.commit()
		return redirect(url_for('.view', load_id=load.id))
	return render_template('load/create.html',
   							title="Create Load",
   							active="Loads",
   							form=form, user=g.user)

@loads.route('/<load_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(load_id):
	permission = EditLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		form = LoadForm()
		if form.validate_on_submit():
			load.load_type = form.load_type.data
			load.trailer_type = form.trailer_type.data
			load.total_miles = form.total_miles.data
			load.price = form.price.data
			load.description = form.description.data
			for location in load.lane.locations:
				db.session.delete(location.address)
				db.session.delete(location.pickup_details)
				db.session.delete(location.delivery_details)
				db.session.delete(location)
			load.lane.locations = []
			broker = Contact.query.filter_by(name=form.broker.company_name.data, 
							phone=form.broker.phone.data, 
							email=form.broker.email.data).first()
			if broker is None:
				broker = ContactFactory(form.broker.company_name.data, 
										form.broker.phone.data, 
										form.broker.email.data)
			
			shipper = Contact.query.filter_by(name=form.shipper.company_name.data, 
									phone=form.shipper.phone.data, 
									email=form.shipper.email.data).first()
			if shipper is None:
				shipper = ContactFactory(form.shipper.company_name.data, 
											form.shipper.phone.data, 
											form.shipper.email.data)

			load.broker = broker
			load.shipper = shipper

			for location in form.locations:

				address = AddressFactory(location.address1.data,
												location.city.data,
												location.state.data,
												location.postal_code.data)
				pickup_detail = LoadDetailFactory(location.pickup_weight.data, "Pickup")
				delivery_detail = LoadDetailFactory(location.delivery_weight.data, "Delivery")
				contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
				stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data, contact, location.stop_type.data)
				load.lane.locations.append(stop_off)
				#db.session.add(stop_off)
				#db.session.add(address)
				#db.session.add(pickup_detail)
				#db.session.add(delivery_detail)
			
			db.session.add(load)
			#db.session.add(load.lane)
			db.session.commit()
		
			return redirect(url_for('.view', load_id=load.id))
		else:
			form.load_type.data = load.load_type
			form.total_miles.data = load.total_miles
			form.trailer_type.data = load.trailer_type
			form.total_miles.data = load.total_miles
			form.price.data = load.price
			form.description.data = load.description
			form.locations = []
			form.broker.company_name.data = load.broker.name
			form.broker.phone.data = load.broker.phone
			form.broker.email.data = load.broker.email
			form.shipper.company_name.data = load.shipper.name
			form.shipper.phone.data = load.shipper.phone
			form.shipper.email.data = load.shipper.email
			for stop_off in load.lane.locations:
				location = LaneLocationForm()
				location.stop_number.data = stop_off.stop_number
				location.address1.data = stop_off.address.address1
				location.city.data = stop_off.address.city
				location.state.data = stop_off.address.state
				location.postal_code.data = stop_off.address.postal_code
				location.pickup_weight.data = stop_off.pickup_details.weight
				location.delivery_weight.data = stop_off.delivery_details.weight

				form.locations.append(location)
			
			form.price.data = load.price

		return render_template('load/edit.html', 
								title="Edit Load", 
								form=form, 
								active="Loads",
								load=load,
								user=g.user)

	abort(403)  # HTTP Forbidden


#View Load
@loads.route('/<load_id>/view', methods=['GET', 'POST'])
@login_required
def view(load_id):
	permission = ViewLoadPermission(load_id)
	
	if permission.can():
		status_form = StatusForm()
		#gn = geocoders.GeoNames()
		#gn.geocode(filter((lambda location: location.is_origin), load.lane.locations)[0].postal_code)
		load = Load.query.get(int(load_id))
		status_form.validate()
		if status_form.validate_on_submit():
			for status in status_form.location_status:
				location = Location.query.filter_by(id=status.location_id.data).first_or_404()
				location.status = status.status.data

			#load.status = status_form.status.data
			db.session.add(load)
			db.session.commit()
		#TODO: filter by applicabale carriers
		if not g.user.is_carrier():
			carriers = []
			for carrier in User.query.all():
				if filter((lambda role: role.name == 'carrier'), carrier.roles):
					carriers.append(carrier)

		else:
			carriers = filter((lambda truck: truck.driver is not None
												and truck.trailer_type == load.trailer_type), 
												g.user.fleet.trucks)
		
		return render_template('load/view.html', status_form=status_form,
												load=load, 
												carriers=carriers,
												locations = load.lane.locations,
												is_dispatch=g.user.is_carrier(),
												title="View Load",
												active="Loads",
												user=g.user)
	abort(403)

@loads.route('/<load_id>/location', methods=['POST', 'GET'])
@login_required
def add_location(load_id):
	permission = EditLoadPermission(load_id)
	if permission.can():
		
		form = LaneLocationForm()
		if form.validate_on_submit():
			load = Load.query.get(int(load_id))
			address = AddressFactory(form.address1.data,
									form.city.data,
									form.state.data,
									form.postal_code.data)
			pickup_detail = LoadDetailFactory(form.pickup_weight.data, "Pickup")
			delivery_detail = LoadDetailFactory(form.delivery_weight.data, "Delivery")
			contact = ContactFactory(form.contact_name.data, form.contact_phone.data, form.contact_email.data)
			stop_off = LocationFactory(address, pickup_detail, delivery_detail, form.arrival_date.data, load.lane.locations.count() + 1, contact, form.stop_type.data)
			load.lane.locations.append(stop_off)
			db.session.add(load)
			db.session.commit()
			return redirect(url_for('.view', load_id=load.id))

		return render_template('load/location/create.html', 
								title="Add Location", 
								form=form, 
								active="Loads",
								user=g.user)

	abort(403)  # HTTP Forbidden

@loads.route('/<load_id>/location/<location_id>', methods=['POST', 'GET'])
@login_required
def edit_location(load_id, location_id):
	permission = EditLoadPermission(load_id)
	if permission.can():
		
		form = LaneLocationForm()
		form.validate()
		flash(form.errors)
		if form.validate_on_submit():
			location = Location.query.get(int(location_id))
			location.address.address1 = form.address1.data
			location.address.city = form.city.data
			location.address.state = form.state.data
			location.address.postal_code = form.postal_code.data
			location.pickup_details.weight = form.pickup_weight.data
			location.pickup_details.notes = form.pickup_notes.data
			location.delivery_details.weight = form.delivery_weight.data
			location.delivery_details.notes = form.delivery_notes.data
			location.contact.name = form.contact_name.data
			location.contact.phone = form.contact_phone.data
			location.contact.email = form.contact_email.data
			location.arrival_date = form.arrival_date.data
			location.type = form.stop_type.data
			db.session.add(location)
			db.session.commit()
			return redirect(url_for('.view', load_id=load_id))

		location = Location.query.get(int(location_id))
		form.address1.data = location.address.address1
		form.city.data = location.address.city
		form.state.data = location.address.state 
		form.postal_code.data = location.address.postal_code
		form.pickup_weight.data = location.pickup_details.weight
		form.pickup_notes.data = location.pickup_details.notes
		form.delivery_weight.data = location.delivery_details.weight
		form.delivery_notes.data = location.delivery_details.notes
		form.contact_name.data = location.contact.name
		form.contact_phone.data = location.contact.phone 
		form.contact_email.data = location.contact.email 
		form.arrival_date.data = location.arrival_date
		form.stop_type.data = location.type

		return render_template('load/location/edit.html', 
								title="Edit Location", 
								form=form, 
								active="Loads",
								user=g.user)

	abort(403)  # HTTP Forbidden

@loads.route('/<load_id>/location/<location_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_location(load_id, location_id):
	permission = EditLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		location = Location.query.get(int(location_id))
		for loc in filter((lambda curLoc: curLoc.stop_number > location.stop_number), load.lane.locations):
			loc.stop_number = int(loc.stop_number) - 1
			db.session.add(loc)
		db.session.delete(location)
		db.session.commit()
		
		return redirect(url_for('.view', load_id=load.id))

	abort(403)  # HTTP Forbidden

@loads.route('/all')
@login_required
def all():
	#loads = Load.query.all()
	#return render_template('load/all.html', loads=loads)
	
	#TODO: if user is a broker - return all loads the broker created
	#return render_template('load/all.html', loads=g.user.loads)
	#TODO: if the user is a carrier - return all loads that have one of their
	#fleet memebers assigned
	#if g.user.is_carrier():
	#	loads = []
	#	for load in Load.query.all():
	#		if load.status == "Assigned" and load.carrier == g.user:
	#			loads.append(load)
	#		else:
	#			for bid in load.bids:
	#				if bid.offered_to == g.user:
	#					loads.append(load)
	#	loads.append(g.user.brokered_loads)
	#	return render_template('load/all.html', loads=loads)
	#else:
	return render_template('load/all.html', 
							loads=g.user.loads, 
							user=g.user, 
							active="Loads",
							title="All Loads")

@loads.route('/<load_id>/delete', methods=['POST', 'GET'])
@login_required
def delete(load_id):
	permission = DeleteLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		db.session.delete(load)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)  # HTTP Forbidden


@loads.route('/<load_id>/assign/<assign_id>', methods=['POST', 'GET'])
@login_required
def assign(load_id, assign_id):
	permission = AssignLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		#If current user is a carrier: remove all other currently assigned carriers and indicate 
		#the load is assigned
		truck = Truck.query.get(assign_id)
		load.assigned_driver = truck.driver
		load.status = "Driver Assigned"
		db.session.add(truck)
		db.session.add(load)
		db.session.commit()
		return redirect(url_for('.view', load_id = load.id))
	abort(403)

@loads.route('/<load_id>/complete', methods=['POST', 'GET'])
@login_required
def complete(load_id):
	permission = CompleteLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		load.assigned_driver.truck.is_available = True
		load.status = "Load Complete"
		db.session.add(load)
		db.session.add(load.assigned_driver)
		db.session.commit()

		return redirect(url_for('.view', load_id = load.id))
	abort(403)

@app.errorhandler(404)
def not_found_error(error):
	app.logger.exception(error)
	return render_template('404.html', user=g.user), 404

@app.errorhandler(404)
def not_found_error(error):
	app.logger.exception(error)
	return render_template('404.html', user=g.user), 404

@app.errorhandler(500)
def internal_error(error):
	print error
	app.logger.exception(error)
	db.session.rollback()
	return render_template('500.html', user=g.user, error=error), 500

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
	if hasattr(current_user, 'loads'):
		for load in current_user.loads:
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
