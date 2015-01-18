from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, abort
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from geopy import geocoders 
from geopy.geocoders import Nominatim
from app import db, lm, app, SQLAlchemy
from app.forms import LoadForm, BidForm, StatusForm
from app.models import Load, LoadDetail, Lane, Location, Truck, User, Bid, Driver
from app.permissions import *
#from app.factories
from sqlalchemy import desc


load = Blueprint('load', __name__, url_prefix='/load')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@load.before_request
def before_request():
	g.user = current_user

@load.route('/create', methods=['GET', 'POST'])
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
		#
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
		#db.session.add(load)
		#db.session.add(g.user)
		#db.session.commit()
		return redirect(url_for('.view', load_id=load.id))
	return render_template('load/create.html',
   							title="Create Load",
   							form=form, user=g.user)

@load.route('/<load_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(load_id):
	permission = EditLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		form = LoadForm()
		if form.validate_on_submit():

			geolocator = Nominatim()
			load_detail = load.load_detail
			origin = load.lane.origin
			destination = load.lane.destination

			origin.address1 = form.origin_address1.data
			origin.address2 = form.origin_address2.data
			origin.city = form.origin_city.data
			origin.state = form.origin_state.data
			origin.postal_code = form.origin_postal_code.data
			origin.contact_phone = form.origin_contact_phone.data
			origin.contact_phone_area_code = form.origin_contact_phone_area_code.data
			origin.contact_phone_prefix = form.origin_contact_phone_prefix.data
			origin.contact_phone_line_number = form.origin_contact_phone_line_number.data
			origin.contact_email = form.origin_contact_email.data
			origin.contact_name = form.origin_contact_name.data
			location = geolocator.geocode(origin.postal_code)
			origin.latitude = location.latitude
			origin.longitude = location.longitude
			destination.address1 = form.destination_address1.data
			destination.address2 = form.destination_address2.data
			destination.city = form.destination_city.data
			destination.state = form.destination_state.data
			destination.postal_code = form.destination_postal_code.data
			destination.contact_phone_area_code = form.origin_contact_phone_area_code.data
			destination.contact_phone_prefix = form.origin_contact_phone_prefix.data
			destination.contact_phone_line_number = form.origin_contact_phone_line_number.data
			destination.contact_email = form.destination_contact_email.data
			destination.contact_name = form.destination_contact_name.data
			location = geolocator.geocode(destination.postal_code)
			destination.latitude = location.latitude
			destination.longitude = location.longitude
			load.load_detail.weight = form.weight.data
			load.load_detail.dim_width = form.dim_width.data
			load.load_detail.dim_length = form.dim_length.data
			load.load_detail.dim_height = form.dim_height.data
			load.load_detail.pickup_date = form.pickup_date.data
			load.load_detail.delivery_date = form.delivery_date.data
			load.load_detail.comments = form.comments.data
			load.load_detail.number_pieces = form.number_pieces.data
			load.load_detail.trailer_type = form.trailer_type.data
			load.load_detail.load_type = form.load_type.data
			load.load_detail.total_miles = form.total_miles.data
			load.name = form.name.data
			load.price = form.price.data
			load.description = form.description.data
			load.load_detail.purchase_order = form.purchase_order.data
			load.load_detail.over_dimensional = form.over_dimensional.data
			if g.user.is_carrier:
				load.carrier_cost = form.price.data
			db.session.add(load_detail)
			db.session.add(origin)
			db.session.add(destination)
			db.session.add(load)

			db.session.commit()
			return redirect(url_for('.all'))
		else:
			load_detail = load.load_detail
			origin = load.lane.origin
			destination = load.lane.destination

			form.origin_address1.data = origin.address1
			form.origin_address2.data = origin.address2
			form.origin_city.data = origin.city
			form.origin_state.data = origin.state
			form.origin_postal_code.data = origin.postal_code
			form.origin_latitude.data = origin.latitude
			form.origin_longitutde = origin.longitude
			form.origin_contact_phone.data = origin.contact_phone
			form.origin_contact_email.data = origin.contact_email
			form.origin_contact_name.data = origin.contact_name
			form.origin_contact_phone_area_code.data = origin.contact_phone_area_code
			form.origin_contact_phone_prefix.data = origin.contact_phone_prefix
			form.origin_contact_phone_line_number.data = origin.contact_phone_line_number
			form.destination_address1.data = destination.address1
			form.destination_address2.data = destination.address2
			form.destination_city.data = destination.city
			form.destination_state.data = destination.state
			form.destination_postal_code.data = destination.postal_code
			form.destination_contact_phone.data = destination.contact_phone
			form.destination_contact_email.data = destination.contact_email
			form.destination_contact_name.data = destination.contact_name
			form.destination_contact_phone_area_code.data = destination.contact_phone_area_code
			form.destination_contact_phone_prefix.data = destination.contact_phone_prefix
			form.destination_contact_phone_line_number.data = destination.contact_phone_line_number
			form.description.data = load.description
			form.purchase_order.data = load.load_detail.purchase_order
			form.over_dimensional.data = load.load_detail.over_dimensional
			form.weight.data = load.load_detail.weight
			form.dim_width.data = load.load_detail.dim_width
			form.dim_length.data = load.load_detail.dim_length
			form.dim_height.data = load.load_detail.dim_height
			#form.pickup_date.data = load.load_detail.pickup_date
			#form.delivery_date.data = load.load_detail.delivery_date
			form.comments.data = load.load_detail.comments
			form.number_pieces.data = load.load_detail.number_pieces
			form.name.data = load.name
			form.pickup_date.data = load.load_detail.pickup_date
			form.delivery_date.data = load.load_detail.delivery_date
			form.trailer_type.data = load.load_detail.trailer_type
			form.load_type.data = load.load_detail.load_type
			form.total_miles.data = load.load_detail.total_miles
			form.price.data = load.price

		return render_template('load/edit.html', title="Edit Load", form=form, load=load, user=g.user)

	abort(403)  # HTTP Forbidden

@load.route('/<load_id>/view', methods=['GET', 'POST'])
@login_required
def view(load_id):
	permission = ViewLoadPermission(load_id)
	if permission.can():
		bid_form = BidForm()
		status_form = StatusForm()
		#gn = geocoders.GeoNames()
		#gn.geocode(filter((lambda location: location.is_origin), load.lane.locations)[0].postal_code)
		load = Load.query.get(int(load_id))
		if status_form.validate_on_submit():
			load.status = status_form.status.data
			db.session.add(load)
			db.session.commit()
		if load.status is not "Pending Truck Assignment":
			status_form.status.data = load.status
		#TODO: filter by applicabale carriers
		if not g.user.is_carrier():
			carriers = []
			for carrier in User.query.all():
				if filter((lambda role: role.name == 'carrier'), carrier.roles):
					carriers.append(carrier)

			for bid in load.bids:
				carriers = filter((lambda carrier: carrier != bid.offered_to), carriers)
		else:
			carriers = filter((lambda truck: truck.is_available 
												and truck.trailer_type == load.load_detail.trailer_type), 
												g.user.fleet.trucks)
		################################

		#if load.status == "Assigned" or load.status == "Complete":
		#	carriers = load.assigned_carriers
		#elif filter((lambda role: role.name == 'carrier'), g.user.roles):
		#	carriers = filter((lambda carrier: carrier.dispatcher.email == g.user.email), load.assigned_carriers)
		rejected_bids = filter((lambda bid: bid.status=="Rejected"), load.bids)
		offered_bids = filter((lambda bid: bid.status=="Offered"), load.bids)
		requested_bids = filter((lambda bid: bid.status=="Requested"), load.bids)
		for rejected_bid in rejected_bids:
			offered_bids = filter((lambda bid: bid.offered_by != rejected_bid.offered_by), offered_bids)
			requested_bids = filter((lambda bid: bid.offered_to != rejected_bid.offered_by), requested_bids)
		for offered_bid in offered_bids:
			requested_bids = filter((lambda bid: bid.offered_to != offered_bid.offered_by), requested_bids)
		offered_bids = filter((lambda bid: bid.status=="Offered"), load.bids)
		return render_template('load/view.html', status_form=status_form,
												bid_form=bid_form,
												load=load, 
												carriers=carriers,
												origin = load.lane.origin,
												destination = load.lane.destination,
												rejected_bids=rejected_bids,
												offered_bids=offered_bids,
												requested_bids=requested_bids,
												most_recent_bid=Bid.query.filter_by(offered_by=g.user).filter_by(load_id=load.id).order_by(desc(Bid.id)).first(),
												is_dispatch=g.user.is_carrier(), 
												user=g.user)
	abort(403)

@load.route('/all')
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
	return render_template('load/all.html', loads=g.user.brokered_loads, user=g.user)

@load.route('/<load_id>/delete', methods=['POST', 'GET'])
@login_required
def delete(load_id):
	permission = DeleteLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		load_detail = load.load_detail
		lane = load.lane
		origin = lane.origin
		destination = lane.destination
		db.session.delete(load)
		db.session.delete(load_detail)
		db.session.delete(lane)
		db.session.delete(origin)
		db.session.delete(destination)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)  # HTTP Forbidden

@load.route('/<load_id>/bid/<company_name>', methods=['POST', 'GET'])
@login_required
def bid(load_id, company_name):
	permission = AssignLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		form = BidForm()
		offered_to = User.query.filter_by(company_name=company_name).first()
		bid = Bid(offered_by=g.user,
					offered_to=offered_to)
		bid.value = 0
		bid.status = "Requested"
		if form.validate_on_submit():
			bid.value = form.value.data
			bid.status = "Offered"
		#offered_to.loads.append(load)
		load.bids.append(bid)
		db.session.add(offered_to)
		db.session.add(bid)
		db.session.add(load)
		db.session.commit()
		return redirect(url_for('.view', load_id = load.id))
	abort(403)

@load.route('/<load_id>/reject/<company_name>', methods=['POST', 'GET'])
@login_required
def reject(load_id, company_name):
	permission = AssignLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		offered_to = User.query.filter_by(company_name=company_name).first()
		bid = Bid(offered_by=g.user,
					offered_to=offered_to)
		bid.value = 0
		bid.status = "Rejected"
		load.bids.append(bid)
		db.session.add(bid)
		db.session.add(load)
		db.session.commit()
		return redirect(url_for('.view', load_id = load.id))
	abort(403)


@load.route('/<load_id>/assign/<assign_id>', methods=['POST', 'GET'])
@login_required
def assign(load_id, assign_id):
	permission = AssignLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		#If current user is a carrier: remove all other currently assigned carriers and indicate 
		#the load is assigned
		if g.user.is_carrier():
			truck = Truck.query.get(assign_id)
			load.assigned_driver = truck.driver
			truck.is_available = False
			load.status = "Driver Assigned"
			db.session.add(truck)
			db.session.add(load)
		#If current user is a broker:
		#	1. 
		else:
			load = Load.query.get(int(load_id))

			#Determine who the broker is
			broker = load.broker
		
			#Retrieve carrier to add to assigned users
			carrier = User.query.filter_by(company_name=assign_id).first()
			bid = Bid.query.filter_by(offered_by=carrier).filter_by(load_id=load.id).order_by(desc(Bid.id)).first()
			load.carrier = carrier
			load.carrier_cost = bid.value
			db.session.add(load)
			db.session.add(carrier)

			#check if broker & dispatcher are contacts.
			#add to contacts if they are not already contacts
			#if not filter((lambda user: user.email == broker.email), carrier.contacts):
			#	carrier.contacts.append(broker)
			#	broker.contacts.append(carrier)
			db.session.add(carrier)
			db.session.add(broker)
			load.status = "Pending Truck Assignment"
			db.session.add(load)
		db.session.commit()
		return redirect(url_for('.view', load_id = load.id))
	abort(403)

@load.route('/<load_id>/complete', methods=['POST', 'GET'])
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

@load.route('/db')
@login_required
def view_db():
	users = User.query.all()
	loads = Load.query.all()
	lanes = Lane.query.all()
	load_details = LoadDetail.query.all()
	locations = Location.query.all()
	return render_template('load/see_db.html', loads=loads, 
							lanes=lanes, 
							load_details=load_details, 
							locations=locations, user=g.user)

@app.errorhandler(404)
def not_found_error(error):
	app.logger.exception(error)
	return render_template('404.html', user=g.user), 404

@app.errorhandler(500)
def internal_error(error):
	print error
	app.logger.exception(error)
	db.session.rollback()
	return render_template('500.html', user=g.user), 500

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