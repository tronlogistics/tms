from app import app
from app import db
from app.repositories.addressrepository import AddressDI
from app.repositories.contactrepository import ContactDI
from app.models.location import Location

class LocationDI():
	@staticmethod
	def createLocationFromForm(form):
		address = AddressDI.createAddressFromForm(form)
		contact = ContactDI.createContactFromForm(form)
		stop_off = Location(address, form.arrival_date.data, form.stop_number.data, contact, form.stop_type.data, form.notes.data)
		return stop_off

	#TODO - this method should not be here
	@staticmethod
	def findMatchingBOLByNumber(pickup_locations, form):
		for loc in pickup_locations:
			for this_BOL in loc.BOLs:
				if this_BOL.number == form.bol_number.data:
					return this_BOL