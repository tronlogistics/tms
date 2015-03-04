from app import db
from geopy import geocoders 
from geopy.geocoders import Nominatim
from app.models import Load, LoadDetail, Lane, Location, Address, Contact
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
				price=form.price.data, 
				description=form.description.data,
				trailer_type=form.trailer_type.data,
				load_type=form.load_type.data,
				total_miles=form.total_miles.data,
				comments=form.comments.data) 
	
	load.assigned_driver = None

	stop_off_locations = []
	locations = filter(lambda location: not location.retired == 0, form.locations)
	for location in locations:
		address = AddressFactory(location.address1.data,
										location.city.data,
										location.state.data,
										location.postal_code.data)
		pickup_detail = LoadDetailFactory(location.pickup_weight.data, "Pickup")
		delivery_detail = LoadDetailFactory(location.delivery_weight.data, "Delivery")
		contact = ContactFactory(location.contact_name.data, location.contact_phone.data, location.contact_email.data)
		stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data, contact, location.stop_type.data)
		stop_off_locations.append(stop_off)

	load.lane = LaneFactory(stop_off_locations)

	return load

def LaneFactory(locations):
	return Lane(locations=locations)


def LocationFactory(address, pickup_detail, delivery_detail, arrival_date, stop_number, contact, stop_type):
	return Location(address=address, 
					pickup_details = pickup_detail, 
					delivery_details= delivery_detail,
					arrival_date=arrival_date,
					stop_number=stop_number,
					contact=contact,
					type=stop_type)


def LoadDetailFactory(weight, type):
	return LoadDetail(weight=weight, type=type)

def AddressFactory(address1, city, state, postal_code):
	return Address(address1=address1,
					city=city,
					state=state,
					postal_code=postal_code)

def ContactFactory(name, email, phone):
	return Contact(name=name,
					phone=email,
					email=phone)