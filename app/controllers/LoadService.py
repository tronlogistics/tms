from app import db, app
from geopy import geocoders 
from geopy.geocoders import Nominatim
from app.models import Load, LoadDetail, Lane, Location, Address, Contact
import urllib
import urllib2
import json
from datetime import datetime

def PostLoadFactory(form, user):
	broker = ContactFactory(user.company.name,
							user.phone,
							user.email)
	shipper = None
	load = Load(broker=broker,
				shipper=shipper,
				name=form.name.data, 
				broker_invoice=0, 
				description="",
				over_dimensional=form.over_dimensional.data,
				trailer_type=form.trailer_type.data,
				load_type=form.load_type.data,
				total_miles=form.total_miles.data,
				max_weight=form.max_weight.data,
				max_length=form.max_length.data,
				max_length_type=form.max_length_type.data,
				max_width=form.max_width.data,
				max_width_type=form.max_width_type.data,
				max_height=form.max_height.data,
				max_height_type=form.max_height_type.data)

	load.assigned_driver = None

	stop_off_locations = []
	locations = filter(lambda location: not location.retired == 0, form.locations)
	for location in locations:
		address = AddressFactory("",
								location.city.data,
								location.state.data,
								location.postal_code.data)
		if(location.stop_type.data == "Pickup" or location.stop_type.data == "Both"):
			pickup_detail = LoadDetailFactory(0, "", "Pickup")
		if(location.stop_type.data == "Pickup" or location.stop_type.data == "Both"):
			delivery_detail = LoadDetailFactory(0, "", "Delivery")
		#contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
		url = 'https://maps.googleapis.com/maps/api/geocode/json?' + urllib.urlencode({
				'address': address.toString()
			}) + "&key=AIzaSyBUCQyghcP_W51ad0aqyZgEYhD-TCGbrQg"

		response = urllib2.urlopen(url)
		data = response.read()
		try: 
			js = json.loads(str(data))
		except: js = None
		if 'status' not in js or js['status'] != 'OK':
			app.logger.error("Failed to Retrieve")


		latitude = js["results"][0]["geometry"]["location"]["lat"]
		longitude = js["results"][0]["geometry"]["location"]["lng"]
		stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data, None, location.stop_type.data, latitude, longitude)
		stop_off_locations.append(stop_off)

	load.lane = LaneFactory(stop_off_locations)
	#shipper.shipped_loads.append(load)
	#broker.brokered_loads.append(load)
	return load

def LoadFactory(form):
	#geolocator = Nominatim
	#load = Load(name=form.name.data, 
	#			price=form.price.data, 
	#			description=form.description.data) 
	#if g.user.is_carrier:
	#	load.status="Pending Truck Assignment"
	#	load.carrier=g.user
	#	load.carrier_cost=form.price.data
	#else:
	#	load.status="Unassigned"
	#load.assigned_driver = None
	#db.session.add(load)
	#lane = Lane
	#load.lane = lane
	#g.user.brokered_loads.append(load)

	#for location in form.locations:
	#	stop_off = Location
	#	address = Address(address1=location.address1.data,
	#							city=location.city.data,
	#							state=location.state.data,
	#							postal_code=location.postal_code.data)
	#	stop_off.address = address
	#	pickup_detail = LoadDetail(weight = form.pickup_weight.data)
	#	delivery_detail = LoadDetail(weight = form.deliver_weight.data)
	#	stop_off.pickup_detail = pickup_detail	
	#	lane.locations.append(stop_off)		

	#db.session.add(load_detail)
	#load.lane = lane
	#load.load_detail = load_detail
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

	load = Load(broker=broker,
				shipper=shipper,
				name=form.name.data, 
				broker_invoice=form.price.data, 
				description=form.description.data,
				trailer_type=form.trailer_type.data,
				load_type=form.load_type.data,
				total_miles=form.total_miles.data) 
	
	load.assigned_driver = None

	stop_off_locations = []
	locations = filter(lambda location: not location.retired == 0, form.locations)
	for location in locations:
		address = AddressFactory(location.address1.data,
										location.city.data,
										location.state.data,
										location.postal_code.data)
		if(location.pickup_weight.data.strip('\t\n\r') is not None):
			pickup_detail = LoadDetailFactory(location.pickup_weight.data, location.pickup_notes.data, "Pickup")
		if(location.delivery_weight.data.strip('\t\n\r') is not None):
			delivery_detail = LoadDetailFactory(location.delivery_weight.data, location.delivery_notes.data, "Delivery")
		contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
		stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data, contact, location.stop_type.data)
		stop_off_locations.append(stop_off)

	load.lane = LaneFactory(stop_off_locations)
	shipper.shipped_loads.append(load)
	broker.brokered_loads.append(load)
	return load

def LaneFactory(locations):
	return Lane(locations=locations)


def LocationFactory(address, pickup_detail, delivery_detail, arrival_date, stop_number, contact, stop_type, latitude, longitude):
	return Location(address=address, 
					pickup_details = pickup_detail, 
					delivery_details= delivery_detail,
					arrival_date=datetime.strptime(arrival_date, "%m-%d-%Y").date(),
					stop_number=stop_number,
					contact=contact,
					type=stop_type,
					latitude=latitude,
					longitude=longitude)


def LoadDetailFactory(weight, notes, type):
	return LoadDetail(weight=weight, notes=notes, type=type)

def PostLoadDetailFactory(weight, notes, type, dim_length, dim_width, dim_height, dim_length_type, dim_width_type, dim_height_type):
	return LoadDetail(weight=weight, notes=notes, type=type, 
						dim_length=dim_length, dim_width=dim_width, dim_height=dim_height,
						dim_length_type=dim_length_type, dim_width_type=dim_width_type,
						dim_height_type=dim_height_type)

def AddressFactory(address1, city, state, postal_code):
	return Address(address1=address1,
					city=city,
					state=state,
					postal_code=postal_code)

def ContactFactory(name, email, phone):
	return Contact(name=name,
					phone=email,
					email=phone)