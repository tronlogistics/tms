from app import db, app
from geopy import geocoders 
from geopy.geocoders import Nominatim
from app.models import Load, LoadDetail, Lane, Location, Address, Contact, BOL
import urllib
import urllib2
import json
from datetime import datetime

def PostLoadFactory(form, user):
	broker = ContactFactory(user.name,
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
		address = AddressFactory(location.address1.data,
								location.city.data,
								location.state.data,
								location.postal_code.data)
		if(location.stop_type.data == "Pickup" or location.stop_type.data == "Both"):
			pickup_detail = LoadDetailFactory(0, "", "Pickup")
		if(location.stop_type.data == "Pickup" or location.stop_type.data == "Both"):
			delivery_detail = LoadDetailFactory(0, "", "Delivery")
		#contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
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

		stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data, None, location.stop_type.data, "", latitude, longitude)
		stop_off_locations.append(stop_off)

	load.lane = LaneFactory(stop_off_locations)
	#shipper.shipped_loads.append(load)
	#broker.brokered_loads.append(load)
	return load

def CreateLoadFactory(form, user):
	#broker = ContactFactory(user.company.name,
	#						user.phone,
	#						user.email)

	broker = None
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
	locations = filter(lambda location: not location.retired == "0", form.locations)
	for location in locations:
		address = AddressFactory(location.address1.data,
								location.city.data,
								location.state.data,
								location.postal_code.data)
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

		stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data, contact, location.stop_type.data, location.notes.data, latitude, longitude)
		stop_off_locations.append(stop_off)
		bols = []
		for cur_BOL in filter(lambda b: not b.retired == "0", location.BOLs):
			bol = None
			if location.stop_type.data == "Drop Off":
				locs = filter((lambda loc: loc.type == "Pickup"), stop_off_locations)
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
			stop_off.BOLs.append(bol)
			db.session.add(bol)

	load.lane = LaneFactory(stop_off_locations)
	#shipper.shipped_loads.append(load)
	#broker.brokered_loads.append(load)
	return load

def LaneFactory(locations):
	return Lane(locations=locations)


def LocationFactory(address, pickup_detail, delivery_detail, arrival_date, stop_number, contact, stop_type, notes, latitude, longitude):
	if type(arrival_date) is str:
		return Location(address=address, 
					pickup_details = pickup_detail, 
					delivery_details= delivery_detail,
					arrival_date=datetime.strptime(arrival_date, "%m-%d-%Y").date(),
					stop_number=stop_number,
					contact=contact,
					type=stop_type,
					notes=notes,
					latitude=latitude,
					longitude=longitude)
	else:
		return Location(address=address, 
					pickup_details = pickup_detail, 
					delivery_details= delivery_detail,
					arrival_date=arrival_date,
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

def BOLFactory(number, number_units, weight, commodity_type, dim_length, dim_length_type, dim_width,
					dim_width_type, dim_height, dim_height_type):
	return BOL(number=number, 
				number_units=number_units, 
				weight=weight, 
				commodity_type=commodity_type, 
				dim_length=dim_length, 
				dim_length_type=dim_length_type, 
				dim_width=dim_width,
				dim_width_type=dim_width_type, 
				dim_height=dim_height, 
				dim_height_type=dim_height_type)