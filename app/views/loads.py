from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, abort
from flask.ext import excel
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, SQLAlchemy
from app.forms import LoadForm, StatusForm, LaneLocationForm, LocationStatusForm
from app.models import Load, LoadDetail, Lane, Location, Truck, User, Driver, Contact
from app.permissions import *
from ..controllers import LoadService, factory
from app.controllers.LoadService import *
from sqlalchemy import desc
from geopy import geocoders 
from geopy.geocoders import Nominatim
import urllib
import urllib2
import json



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
			
			
			form.price.data = load.price

		return render_template('load/edit.html', 
								title="Edit Load", 
								form=form, 
								active="Loads",
								load=load,
								user=g.user,
								edit=True)

	abort(403)  # HTTP Forbidden


#View Load
@loads.route('/<load_id>/view', methods=['GET', 'POST'])
@login_required
def view(load_id):
	permission = ViewLoadPermission(load_id)
	
	if permission.can():
		#gn = geocoders.GeoNames()
		#gn.geocode(filter((lambda location: location.is_origin), load.lane.locations)[0].postal_code)
		load = Load.query.get(int(load_id))

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
		sorted_locations = sorted(filter((lambda location: location.stop_number > 0), 
												load.lane.locations), key=lambda location: location.stop_number, reverse=False)
		if len(sorted_locations) == 0:
			if load.lane.locations.count() == 0:
				current_location = None
			else:
				current_location = load.lane.locations[-1]
		else:
			current_location = sorted_locations[0]
		return render_template('load/view2.html',
												load=load, 
												carriers=carriers,
												locations = load.lane.locations,
												is_dispatch=g.user.is_carrier(),
												title="View Load",
												active="Loads",
												current_location=current_location,
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
			url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
					'address': address.toString()
				}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"
			response = urllib2.urlopen(url)
			data = response.read()
			try: js = json.loads(str(data))
			except: js = None
			if 'status' not in js or js['status'] != 'OK':
				app.logger.error("Failed to Retrieve")


			latitude = js["results"][0]["geometry"]["location"]["lat"]
			app.logger.info(latitude)
			longitude = js["results"][0]["geometry"]["location"]["lng"]
			app.logger.info(longitude)
			if(form.pickup_weight.data.strip('\t\n\r') != ""):
				app.logger.info('creating pickup')
				pickup_detail = LoadDetailFactory(form.pickup_weight.data, form.pickup_notes.data, "Pickup")
			else:
				pickup_detail = None
			if(form.delivery_weight.data.strip('\t\n\r') != ""):
				app.logger.info('creating delivery')
				delivery_detail = LoadDetailFactory(form.delivery_weight.data, form.delivery_notes.data, "Delivery")
			else:
				delivery_detail = None
			contact = ContactFactory(form.contact_name.data, form.contact_phone.data, form.contact_email.data)
			stop_off = LocationFactory(address, pickup_detail, delivery_detail, form.arrival_date.data, load.lane.locations.count() + 1, contact, form.stop_type.data, latitude, longitude)
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
		if form.validate_on_submit():
			location = Location.query.get(int(location_id))
			location.address.address1 = form.address1.data
			location.address.city = form.city.data
			location.address.state = form.state.data
			location.address.postal_code = form.postal_code.data
			if(form.pickup_weight.data.strip('\t\n\r') != ""):
				if location.pickup_details is None:
					location.pickup_details = LoadDetailFactory(form.pickup_weight.data, form.pickup_notes.data, "Pickup")
				else:
					location.pickup_details.weight = form.pickup_weight.data
					location.pickup_details.notes = form.pickup_notes.data
			else:
				location.pickup_details = None

			if(form.delivery_weight.data.strip('\t\n\r') != ""):
				if location.delivery_details is None:
					location.delivery_details = LoadDetailFactory(form.delivery_weight.data, form.delivery_notes.data, "Pickup")
				else:
					location.delivery_details.weight = form.delivery_weight.data
					location.delivery_details.notes = form.delivery_notes.data
			else:
				location.delivery_details = None
			
			
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
		if location.pickup_details is not None:
			form.pickup_weight.data = location.pickup_details.weight
			form.pickup_notes.data = location.pickup_details.notes
		if location.delivery_details is not None:
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
		load.truck = truck
		load.status = "Assigned"
		db.session.add(truck)
		db.session.add(load)
		db.session.commit()
		return redirect(url_for('.view', load_id = load.id))
	abort(403)

@loads.route('/<load_id>/invoice', methods=['POST', 'GET'])
@login_required
def invoice(load_id):
	permission = InvoiceLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		load.truck.is_available = True
		load.status = "Invoiced"
		db.session.add(load)
		db.session.add(load.truck)
		db.session.commit()

		return redirect(url_for('.all', load_id = load.id))
	abort(403)

@loads.route('/<load_id>/complete', methods=['POST', 'GET'])
@login_required
def complete(load_id):
	permission = CompleteLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		load.truck.is_available = True
		load.status = "Completed"
		db.session.add(load)
		db.session.add(load.truck)
		db.session.commit()

		return redirect(url_for('.view', load_id = load.id))
	abort(403)

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
			identity.provides.add(InvoiceLoadNeed(unicode(load.id)))
			identity.provides.add(CompleteLoadNeed(unicode(load.id)))

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