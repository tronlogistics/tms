from geopy import geocoders 
from geopy.geocoders import Nominatim
from app.models import Load, LoadDetail, Lane, Location, Address
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


	load = Load(name=form.name.data, 
				price=form.price.data, 
				description=form.description.data,
				trailer_type=form.trailer_type.data,
				load_type=form.load_type.data,
				total_miles=form.total_miles.data,
				comments=form.comments.data) 
	
	load.assigned_driver = None

	stop_off_locations = []
	for location in form.locations:
		address = AddressFactory(location.address1.data,
										location.city.data,
										location.state.data,
										location.postal_code.data)
		pickup_detail = LoadDetailFactory(location.pickup_weight.data, "Pickup")
		delivery_detail = LoadDetailFactory(location.delivery_weight.data, "Delivery")
		stop_off = LocationFactory(address, pickup_detail, delivery_detail, location.arrival_date.data, location.stop_number.data)
		stop_off_locations.append(stop_off)

	load.lane = LaneFactory(stop_off_locations)

	return load

def LaneFactory(locations):
	return Lane(locations=locations)


def LocationFactory(address, pickup_detail, delivery_detail, arrival_date, stop_number):
	return Location(address=address, 
					pickup_details = pickup_detail, 
					delivery_details= delivery_detail,
					arrival_date=arrival_date,
					stop_number=stop_number)


def LoadDetailFactory(weight, type):
	return LoadDetail(weight=weight, type=type)

def AddressFactory(address1, city, state, postal_code):
	return Address(address1=address1,
					city=city,
					state=state,
					postal_code=postal_code)