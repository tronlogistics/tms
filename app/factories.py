from app import db
from app.models import *
from geopy import geocoders 
from geopy.geocoders import Nominatim

#class UserFactory:
#	def create_user(form):
#		return User("hi")

class LoadFactory:
	def create_load(form):
		geolocator = Nominatim()
		load = Load(name=form.name.data, 
					price=form.price.data, 
					description=form.description.data) 
		if g.user.is_carrier():
			load.status="Pending Truck Assignment"
			load.carrier=g.user
			load.carrier_cost=form.price.data
		else:
			load.status="Unassigned"
		load.assigned_driver = None
		db.session.add(load)
		g.user.brokered_loads.append(load)



		origin = Location(address1=form.origin_address1.data,
							address2=form.origin_address2.data,
							city=form.origin_city.data,
							state=form.origin_state.data,
							postal_code=form.origin_postal_code.data,
							contact_name=form.origin_contact_name.data,
							contact_email=form.origin_contact_email.data)

		origin.contact_phone_area_code = str(form.origin_contact_phone_area_code.data)
		if len(origin.contact_phone_area_code) < 3:
			prepend_value = ""
			for x in range(0, 3 - len(origin.contact_phone_area_code)):
				prepend_value += "0"
			origin.contact_phone_area_code = prepend_value + origin.contact_phone_area_code
		
		origin.contact_phone_prefix = str(form.origin_contact_phone_prefix.data)
		if len(origin.contact_phone_prefix) < 3:
			prepend_value = ""
			for x in range(0, 3 - len(origin.contact_phone_prefix)):
				prepend_value += "0"
			origin.contact_phone_prefix = prepend_value + origin.contact_phone_prefix
		
		origin.contact_phone_line_number = str(form.origin_contact_phone_line_number.data)
		if len(origin.contact_phone_line_number) < 4:
			prepend_value = ""
			for x in range(0, 4 - len(origin.contact_phone_line_number)):
				prepend_value += "0"
			origin.contact_phone_line_number = prepend_value + origin.contact_phone_line_number

		location = geolocator.geocode(origin.postal_code)
		origin.latitude = location.latitude
		origin.longitude = location.longitude
		db.session.add(origin)
		destination = Location(address1=form.destination_address1.data,
							address2=form.destination_address2.data,
							city=form.destination_city.data,
							state=form.destination_state.data,
							postal_code=form.destination_postal_code.data,
							contact_name=form.destination_contact_name.data,
							contact_email=form.destination_contact_email.data)

		destination.contact_phone_area_code = str(form.destination_contact_phone_area_code.data)
		if len(destination.contact_phone_area_code) < 3:
			prepend_value = ""
			for x in range(0, 3 - len(destination.contact_phone_area_code)):
				prepend_value += "0"
			destination.contact_phone_area_code = prepend_value + destination.contact_phone_area_code
		
		destination.contact_phone_prefix = str(form.destination_contact_phone_prefix.data)
		if len(destination.contact_phone_prefix) < 3:
			prepend_value = ""
			for x in range(0, 3 - len(destination.contact_phone_prefix)):
				prepend_value += "0"
			destination.contact_phone_prefix = prepend_value + destination.contact_phone_prefix
		
		destination.contact_phone_line_number = str(form.destination_contact_phone_line_number.data)
		if len(destination.contact_phone_line_number) < 4:
			prepend_value = ""
			for x in range(0, 4 - len(destination.contact_phone_line_number)):
				prepend_value += "0"
			destination.contact_phone_line_number = prepend_value + destination.contact_phone_line_number
		location = geolocator.geocode(destination.postal_code)
		destination.latitude = location.latitude
		destination.longitude = location.longitude
		db.session.add(destination)
		lane = Lane(origin=origin, destination=destination)
		db.session.add(lane)

		load_detail = LoadDetail(weight = form.weight.data,
								dim_length = form.dim_length.data,
								dim_width = form.dim_width.data,
								dim_height = form.dim_height.data,
								number_pieces = form.number_pieces.data,
								comments = form.comments.data,
								pickup_date=form.pickup_date.data, 
								delivery_date=form.delivery_date.data,
								trailer_type=form.trailer_type.data,
								load_type=form.load_type.data,
								total_miles=form.total_miles.data,
								purchase_order = form.purchase_order.data,
								over_dimensional = form.over_dimensional.data)
		db.session.add(load_detail)
		load.lane = lane
		load.load_detail = load_detail
		load.broker = g.user
		db.session.add(load)
		db.session.add(g.user)
		db.session.commit()
