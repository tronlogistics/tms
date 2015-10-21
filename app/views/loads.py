from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, abort
from flask.ext import excel
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, SQLAlchemy
from app.forms import LoadForm, StatusForm, LaneLocationForm, LocationStatusForm, BidForm, PostLoadForm, AcceptBidForm, BOLForm
from app.models import Load, LoadDetail, Lane, Location, Truck, User, Driver, Contact, Bid, BOL
from app.permissions import *
from app.emails import bid_accepted
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
	form = PostLoadForm()
	if form.validate_on_submit():
		#load = PostLoadFactory(form, g.user)
		#load.created_by = g.user
		#g.user.company.loads.append(load)
		#if g.user.is_carrier:
		#	load.setStatus("")
		#	load.carrier_cost=form.price.data
		#else:
		#	load.setStatus("")
		#db.session.add(load)
		#db.session.add(g.user.company)
		#db.session.commit()
		#return redirect(url_for('.view', load_id=load.id))
		load = CreateLoadFactory(form, g.user)
		load.created_by = g.user
		g.user.company.loads.append(load)
		load.setStatus("")
		db.session.add(load)
		db.session.add(g.user.company)
		db.session.commit()
		return redirect(url_for('.view', load_id=load.id))
	flash(form.errors)
	return render_template('load/create3.html',
   							title="Create Load",
   							active="Loads",
   							form=form, user=g.user)

@loads.route('/post', methods=['GET', 'POST'])
@login_required
def post():
	form = PostLoadForm()
	for location in form.locations:
		location.arrival_date.data = location.arrival_date.data.strftime("%m-%d-%Y")
	if form.validate_on_submit():
		load = PostLoadFactory(form, g.user)
		load.created_by = g.user
		g.user.company.loads.append(load)
		load.setStatus("")
		db.session.add(load)
		db.session.add(g.user.company)
		db.session.commit()
		return redirect(url_for('.view', load_id=load.id))
	return render_template('load/post.html',
   							title="Post Load",
   							active="Loads",
   							form=form, 
   							user=g.user)

@loads.route('/<load_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(load_id):
	permission = EditLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		#form = LoadForm()
		form = PostLoadForm()
		if form.validate_on_submit():
			load.name = form.name.data
			load.load_type = form.load_type.data
			load.total_miles = form.total_miles.data
			load.trailer_type = form.trailer_type.data
			load.total_miles = form.total_miles.data
			load.max_weight = form.max_weight.data
			load.over_dimensional = form.over_dimensional.data
			load.max_length = form.max_length.data
			load.max_length_type = form.max_length_type.data
			load.max_width = form.max_width.data
			load.max_width_type = form.max_width_type.data
			load.max_height = form.max_height.data
			load.max_height_type = form.max_height_type.data

			locations = filter(lambda location: not location.retired == "0", form.locations)
			for index, location in enumerate(locations):
				#print "%s > %s = %s" % (location.stop_number.data, load.lane.locations.count(), int(location.stop_number.data) > int(load.lane.locations.count()))
				if int(location.stop_number.data) > int(load.lane.locations.count()):
					address = AddressFactory(location.address1.data,
											location.city.data,
											location.state.data,
											location.postal_code.data)
					print location.stop_type.data
					if(location.stop_type.data == "Pickup" or location.stop_type.data == "Both"):
						pickup_detail = LoadDetailFactory(0, "", "Pickup")
						delivery_detail = None
					if(location.stop_type.data == "Drop Off" or location.stop_type.data == "Both"):
						pickup_detail = None
						delivery_detail = LoadDetailFactory(0, "", "Delivery")
					contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
					url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
							'address': address
						}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

					response = urllib2.urlopen(url)
					data = response.read()
					try: 
						js = json.loads(str(data))
					except: js = None
					if 'status' not in js or js['status'] != 'OK':
						app.logger.error("Failed to Retrieve")

					latitude = None
					longitude = None
					if len(js["results"]) > 0:
						latitude = js["results"][0]["geometry"]["location"]["lat"]
						longitude = js["results"][0]["geometry"]["location"]["lng"]
					
					new_location = Location(address=address, 
											pickup_details = pickup_detail, 
											delivery_details= delivery_detail,
											arrival_date=location.arrival_date.data,
											stop_number=location.stop_number.data,
											contact=contact,
											type=location.stop_type.data,
											notes=location.notes.data,
											latitude=latitude,
											longitude=longitude)
					load.lane.locations.append(new_location)
					bols = []
					for cur_BOL in filter(lambda b: not b.retired == "0", location.BOLs):
						bol = None
						if location.stop_type.data == "Drop Off":
							locs = filter((lambda loc: loc.type == "Pickup"), load.lane.locations)
							for loc in locs:
								for this_BOL in loc.BOLs:
									if this_BOL.number == cur_BOL.bol_number.data:
										bol = this_BOL
						else:				
							bol = BOL(number=cur_BOL.bol_number.data,
										number_units=cur_BOL.number_units.data,
										weight=cur_BOL.weight.data,
										commodity_type=cur_BOL.commodity_type.data,
										dim_length=cur_BOL.dim_length.data,
										dim_length_type=cur_BOL.dim_length_type.data,
										dim_width=cur_BOL.dim_width.data,
										dim_width_type=cur_BOL.dim_width_type.data,
										dim_height=cur_BOL.dim_height.data,
										dim_height_type=cur_BOL.dim_height_type.data)
						new_location.BOLs.append(bol)
						db.session.add(bol)
					db.session.add(load)
					db.session.commit()
				else:
					load.lane.locations[index].arrival_date = location.arrival_date.data
					load.lane.locations[index].type=location.stop_type.data
					load.lane.locations[index].notes=location.notes.data
					load.lane.locations[index].contact.name = location.contact_name.data
					load.lane.locations[index].contact.phone = location.contact_phone.data
					load.lane.locations[index].address.address1 = location.address1.data
					load.lane.locations[index].address.city = location.city.data
					load.lane.locations[index].address.state = location.state.data
					load.lane.locations[index].address.postal_code = location.postal_code.data
					
					url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
							'address': load.lane.locations[index].address
						}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

					response = urllib2.urlopen(url)
					data = response.read()
					try: 
						js = json.loads(str(data))
					except: js = None
					if 'status' not in js or js['status'] != 'OK':
						app.logger.error("Failed to Retrieve")

					latitude = None
					longitude = None
					if len(js["results"]) > 0:
						latitude = js["results"][0]["geometry"]["location"]["lat"]
						longitude = js["results"][0]["geometry"]["location"]["lng"]
					load.lane.locations[index].latitude = latitude
					load.lane.locations[index].longitude = longitude
					load.lane.locations[index].BOLs = []
					bols = filter(lambda b: not b.retired == "0", location.BOLs)
					for cur_BOL in bols:
						bol = None
						if location.stop_type.data == "Drop Off":
							locs = filter((lambda loc: loc.type == "Pickup"), load.lane.locations)
							for loc in locs:
								for this_BOL in loc.BOLs:
									if this_BOL.number == cur_BOL.bol_number.data:
										bol = this_BOL
						else:				
							bol = BOL(number=cur_BOL.bol_number.data,
										number_units=cur_BOL.number_units.data,
										weight=cur_BOL.weight.data,
										commodity_type=cur_BOL.commodity_type.data,
										dim_length=cur_BOL.dim_length.data,
										dim_length_type=cur_BOL.dim_length_type.data,
										dim_width=cur_BOL.dim_width.data,
										dim_width_type=cur_BOL.dim_width_type.data,
										dim_height=cur_BOL.dim_height.data,
										dim_height_type=cur_BOL.dim_height_type.data)
						load.lane.locations[index].BOLs.append(bol)
						db.session.add(bol)
					db.session.add(load)
					db.session.commit()
						
			return redirect(url_for('.view', load_id=load.id))
		else:
			if len(form.errors) == 0:
				form.name.data = load.name
				form.load_type.data = load.load_type
				form.total_miles.data = load.total_miles
				form.trailer_type.data = load.trailer_type
				form.total_miles.data = load.total_miles
				form.max_weight.data = load.max_weight
				form.over_dimensional.data = load.over_dimensional
				form.max_length.data = load.max_length
				form.max_length_type.data = load.max_length_type
				form.max_width.data = load.max_width
				form.max_width_type.data = load.max_width_type
				form.max_height.data = load.max_height
				form.max_height_type.data = load.max_height_type

				for location in load.lane.locations:
					bols = []
					print location
					for bol in location.BOLs:
						print bol
						bols.append({
							"bol_number": bol.number,
							"number_units": bol.number_units,
							"weight": bol.weight,
							"commodity_type": bol.commodity_type,
							"dim_length": bol.dim_length,
							"dim_length_type": bol.dim_length_type,
							"dim_width": bol.dim_width,
							"dim_width_type": bol.dim_width_type,
							"dim_height": bol.dim_height,
							"dim_height_type": bol.dim_height_type
						})
					loc_data = {
				        "stop_number": location.stop_number,
				        "stop_type": location.type,
						"address1": location.address.address1,
						"city": location.address.city,
						"state": location.address.state,
						"postal_code": location.address.postal_code,
						"arrival_date": location.arrival_date.strftime("%m/%d/%Y"),
						"contact_name": location.contact.name,
						"contact_phone": location.contact.phone,
						"notes":  location.notes,
				        "BOLs": bols
				    }
					

					form.locations.append_entry(loc_data)

				
			#form.price.data = load.carrier_invoice
			#form.description.data = load.description
			#form.locations = []
			#form.broker.company_name.data = load.broker.name
			#form.broker.phone.data = load.broker.phone
			#form.broker.email.data = load.broker.email
			#form.shipper.company_name.data = load.shipper.name
			#form.shipper.phone.data = load.shipper.phone
			#form.shipper.email.data = load.shipper.email

		return render_template('load/edit3.html', 
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

		if g.user.company.is_carrier() and len(load.assigned_companies) < 2 and load.created_by.company != g.user.company:
			return render_template('load/view_hidden.html',
												load=load, 
												carriers=carriers,
												locations = load.lane.locations,
												is_dispatch=g.user.is_carrier(),
												title="View Load",
												active="Loads",
												current_location=current_location,
												user=g.user)
		else:
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
			load.setStatus("")

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
	loads = []

	return render_template('load/all.html', 
							loads=g.user.company.loads, 
							user=g.user, 
							active="Loads",
							title="All Loads")

@loads.route('/board')
@login_required
def board():
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
	all_loads = Load.query.all()
	brokered_loads = filter((lambda load: not load.created_by.company.is_carrier() and len(load.assigned_companies) < 2 and load.status == "Pending Carrier Assignment"), 
											all_loads)
	return render_template('load/all.html', 
							loads=brokered_loads, 
							user=g.user, 
							active="Loads",
							title="Load Board")

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
		load.setStatus("")
		db.session.add(truck)
		db.session.add(load)
		db.session.commit()
		return redirect(url_for('.view', load_id = load.id))
	abort(403)

@loads.route('/<load_id>/unassign/<unassign_id>', methods=['POST', 'GET'])
@login_required
def unassign(load_id, unassign_id):
	permission = AssignLoadPermission(load_id)
	if permission.can():
		load = Load.query.get(int(load_id))
		#If current user is a carrier: remove all other currently assigned carriers and indicate 
		#the load is assigned
		truck = Truck.query.get(unassign_id)
		if truck.id == load.truck.id:
			load.truck = None
			load.setStatus("")
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

@loads.route('/<load_id>/driver', methods=['GET'])
@login_required
def assign_driver(load_id):
	load = Load.query.get(int(load_id))
	#TODO: filter by applicabale carriers
	if not g.user.company.is_carrier():
		carriers = []
		for carrier in User.query.all():
			if filter((lambda role: role.name == 'carrier'), carrier.roles):
				carriers.append(carrier)

	else:
		carriers = filter((lambda truck: truck.driver is not None
											and truck.trailer_type == load.trailer_type), 
											g.user.company.fleet.trucks)

	return render_template('load/assign_driver.html', 
							load=load, 
							carriers=carriers, 
							user=g.user,
							active="Loads",
							hide=True,
							title="Assign Driver")
	abort(403)

@loads.route('/<load_id>/bids/create', methods=['GET', 'POST'])
@login_required
def create_bid(load_id):
	load = Load.query.get(int(load_id))
	form = BidForm()
	if form.validate_on_submit():
		bid = Bid(value=form.value.data, created_by=g.user)
		load.bids.append(bid)
		db.session.add(bid)
		db.session.add(load)
		db.session.commit()
		return redirect(url_for('.board'))
	else:
		return render_template('load/bid/create.html', 
							form=form,
							load=load, 
							user=g.user,
							active="Loads",
							hide=True,
							title="Create Bid")

@loads.route('/<load_id>/bids/<bid_id>/accept', methods=['GET', 'POST'])
@login_required
def accept_bid(load_id, bid_id):
	load = Load.query.get(int(load_id))
	bid = Bid.query.get(int(bid_id))
	form = PostLoadForm()
	if form.validate_on_submit():
		load.name = form.name.data
		load.load_type = form.load_type.data
		load.total_miles = form.total_miles.data
		load.trailer_type = form.trailer_type.data
		load.total_miles = form.total_miles.data
		load.max_weight = form.max_weight.data
		load.over_dimensional = form.over_dimensional.data
		load.max_length = form.max_length.data
		load.max_length_type = form.max_length_type.data
		load.max_width = form.max_width.data
		load.max_width_type = form.max_width_type.data
		load.max_height = form.max_height.data
		load.max_height_type = form.max_height_type.data

		locations = filter(lambda location: not location.retired == "0", form.locations)
		for index, location in enumerate(locations):
			#print "%s > %s = %s" % (location.stop_number.data, load.lane.locations.count(), int(location.stop_number.data) > int(load.lane.locations.count()))
			if int(location.stop_number.data) > int(load.lane.locations.count()):
				address = AddressFactory(location.address1.data,
										location.city.data,
										location.state.data,
										location.postal_code.data)
				print location.stop_type.data
				if(location.stop_type.data == "Pickup" or location.stop_type.data == "Both"):
					pickup_detail = LoadDetailFactory(0, "", "Pickup")
					delivery_detail = None
				if(location.stop_type.data == "Drop Off" or location.stop_type.data == "Both"):
					pickup_detail = None
					delivery_detail = LoadDetailFactory(0, "", "Delivery")
				contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
				url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
						'address': address
					}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

				response = urllib2.urlopen(url)
				data = response.read()
				try: 
					js = json.loads(str(data))
				except: js = None
				if 'status' not in js or js['status'] != 'OK':
					app.logger.error("Failed to Retrieve")

				latitude = None
				longitude = None
				if len(js["results"]) > 0:
					latitude = js["results"][0]["geometry"]["location"]["lat"]
					longitude = js["results"][0]["geometry"]["location"]["lng"]
				
				new_location = Location(address=address, 
										pickup_details = pickup_detail, 
										delivery_details= delivery_detail,
										arrival_date=location.arrival_date.data,
										stop_number=location.stop_number.data,
										contact=contact,
										type=location.stop_type.data,
										notes=location.notes.data,
										latitude=latitude,
										longitude=longitude)
				load.lane.locations.append(new_location)
				bols = []
				for cur_BOL in filter(lambda b: not b.retired == "0", location.BOLs):
					bol = None
					if location.stop_type.data == "Drop Off":
						locs = filter((lambda loc: loc.type == "Pickup"), load.lane.locations)
						for loc in locs:
							for this_BOL in loc.BOLs:
								if this_BOL.number == cur_BOL.bol_number.data:
									bol = this_BOL
					else:				
						bol = BOL(number=cur_BOL.bol_number.data,
									number_units=cur_BOL.number_units.data,
									weight=cur_BOL.weight.data,
									commodity_type=cur_BOL.commodity_type.data,
									dim_length=cur_BOL.dim_length.data,
									dim_length_type=cur_BOL.dim_length_type.data,
									dim_width=cur_BOL.dim_width.data,
									dim_width_type=cur_BOL.dim_width_type.data,
									dim_height=cur_BOL.dim_height.data,
									dim_height_type=cur_BOL.dim_height_type.data)
					new_location.BOLs.append(bol)
					db.session.add(bol)
				db.session.add(load)
				db.session.commit()
			else:
				load.lane.locations[index].arrival_date = location.arrival_date.data
				load.lane.locations[index].type=location.stop_type.data
				load.lane.locations[index].notes=location.notes.data
				load.lane.locations[index].contact.name = location.contact_name.data
				load.lane.locations[index].contact.phone = location.contact_phone.data
				load.lane.locations[index].address.address1 = location.address1.data
				load.lane.locations[index].address.city = location.city.data
				load.lane.locations[index].address.state = location.state.data
				load.lane.locations[index].address.postal_code = location.postal_code.data
				
				url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
						'address': load.lane.locations[index].address
					}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

				response = urllib2.urlopen(url)
				data = response.read()
				try: 
					js = json.loads(str(data))
				except: js = None
				if 'status' not in js or js['status'] != 'OK':
					app.logger.error("Failed to Retrieve")

				latitude = None
				longitude = None
				if len(js["results"]) > 0:
					latitude = js["results"][0]["geometry"]["location"]["lat"]
					longitude = js["results"][0]["geometry"]["location"]["lng"]
				load.lane.locations[index].latitude = latitude
				load.lane.locations[index].longitude = longitude
				load.lane.locations[index].BOLs = []
				bols = filter(lambda b: not b.retired == "0", location.BOLs)
				for cur_BOL in bols:
					bol = None
					if location.stop_type.data == "Drop Off":
						locs = filter((lambda loc: loc.type == "Pickup"), load.lane.locations)
						for loc in locs:
							for this_BOL in loc.BOLs:
								if this_BOL.number == cur_BOL.bol_number.data:
									bol = this_BOL
					else:				
						bol = BOL(number=cur_BOL.bol_number.data,
									number_units=cur_BOL.number_units.data,
									weight=cur_BOL.weight.data,
									commodity_type=cur_BOL.commodity_type.data,
									dim_length=cur_BOL.dim_length.data,
									dim_length_type=cur_BOL.dim_length_type.data,
									dim_width=cur_BOL.dim_width.data,
									dim_width_type=cur_BOL.dim_width_type.data,
									dim_height=cur_BOL.dim_height.data,
									dim_height_type=cur_BOL.dim_height_type.data)
					load.lane.locations[index].BOLs.append(bol)
					db.session.add(bol)
				db.session.add(load)
				db.session.commit()
		bid.created_by.company.loads.append(load)
		bid.accepted = True
		load.setStatus("")
		db.session.add(load)
		db.session.add(bid)
		db.session.add(bid.created_by.company)
		db.session.commit()
		bid_accepted(bid.created_by, load)
					
		return redirect(url_for('.view', load_id=load.id))
	else:
		if len(form.errors) == 0:
			form.name.data = load.name
			form.load_type.data = load.load_type
			form.total_miles.data = load.total_miles
			form.trailer_type.data = load.trailer_type
			form.total_miles.data = load.total_miles
			form.max_weight.data = load.max_weight
			form.over_dimensional.data = load.over_dimensional
			form.max_length.data = load.max_length
			form.max_length_type.data = load.max_length_type
			form.max_width.data = load.max_width
			form.max_width_type.data = load.max_width_type
			form.max_height.data = load.max_height
			form.max_height_type.data = load.max_height_type

			for location in load.lane.locations:
				bols = []
				bols.append({
					"bol_number": "",
					"number_units": "",
					"weight": "",
					"commodity_type": "",
					"dim_length": "",
					"dim_length_type": "",
					"dim_width": "",
					"dim_width_type": "",
					"dim_height": "",
					"dim_height_type": "",
				})
				if location.contact is not None:
					loc_data = {
				        "stop_number": location.stop_number,
				        "stop_type": location.type,
						"address1": location.address.address1,
						"city": location.address.city,
						"state": location.address.state,
						"postal_code": location.address.postal_code,
						"arrival_date": location.arrival_date.strftime("%m/%d/%Y"),
						"contact_name": location.contact.name,
						"contact_phone": location.contact.phone,
						"notes":  location.notes,
				        "BOLs": bols
				    }
				else:
					loc_data = {
				        "stop_number": location.stop_number,
				        "stop_type": location.type,
						"address1": location.address.address1,
						"city": location.address.city,
						"state": location.address.state,
						"postal_code": location.address.postal_code,
						"arrival_date": location.arrival_date.strftime("%m/%d/%Y"),
						"contact_name": "",
						"contact_phone": "",
						"notes":  location.notes,
				        "BOLs": bols
				    }
				

				form.locations.append_entry(loc_data)

			
		#form.price.data = load.carrier_invoice
		#form.description.data = load.description
		#form.locations = []
		#form.broker.company_name.data = load.broker.name
		#form.broker.phone.data = load.broker.phone
		#form.broker.email.data = load.broker.email
		#form.shipper.company_name.data = load.shipper.name
		#form.shipper.phone.data = load.shipper.phone
		#form.shipper.email.data = load.shipper.email

	return render_template('load/edit3.html', 
							title="Create Rate Confirmation", 
							form=form, 
							active="Loads",
							load=load,
							user=g.user,
							edit=True)
	

	#return render_template('load/accept_bid.html', 
	#						form=form,
	#						load=load, 
	#						user=g.user,
	#						active="Loads",
	#						hide=True,
	#						title="Accept Bid")

@loads.route('/<load_id>/bids/<bid_id>/reject', methods=['GET', 'POST'])
@login_required
def reject_bid(load_id, bid_id):
	bid = Bid.query.get(int(bid_id))
	bid.accepted = False
	db.session.add(bid)
	db.session.commit()

	## SEND EMAIL THAT BID HAS BEEN REJECTED


	return redirect(url_for('.board'))

@loads.route('/<load_id>/bids/all', methods=['GET', 'POST'])
@login_required
def view_bids(load_id):
	load = Load.query.get(int(load_id))
	return render_template('load/bid/view_all.html', 
							load=load, 
							bids=filter((lambda bid: bid.accepted != False), load.bids),
							user=g.user,
							active="Loads",
							hide=True,
							title="View Bids")

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