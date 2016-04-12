from app import db, app
from geopy import geocoders 
from geopy.geocoders import Nominatim
from app.models.load import *
from app.models.loaddetail import *
from app.models.lane import *
from app.models.location import *
from app.models.address import *
from app.models.bol import *
import urllib
import urllib2
import json
from datetime import datetime

#Create Load
#Edit Load
#Delete Load

#Assign Driver
#Unassign Driver
#Add History Event

def createLoadFromForm(form, user):
	load = Load.createLoadFromForm(form, user)
	db.session.add(load)
	db.session.commit()
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
					notes=notes,
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