from app import db
from app.models import *
from geopy import geocoders 
from geopy.geocoders import Nominatim

def getNextLocation(truck):
	for load in truck.driver.loads:
		for location in load.lane.location:
			if int(location.stop_number) == 1:
				return location
	return null

def getUpcomingLocations(truck):
	locations = []
	for load in filter(lambda cur: cur.status != "Completed", truck.driver.loads):
		for location in filter(lambda cur: cur.Status != "Departed", load.lane.locations):
			locations.append(location)
	return locations

