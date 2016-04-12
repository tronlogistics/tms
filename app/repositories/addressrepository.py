from app import app
from app import db
from app.models.address import Address

class AddressDI():
	
	@staticmethod
	def createAddressFromForm(form):
		address = Address(address1=form.address1.data,
							city=form.city.data,
							state=form.state.data,
							postal_code=form.postal_code.data)
		return address 

	@staticmethod
	def createAddressFromJSON(json):
		address = Address(address1=json.get('streetAddress'),
							city=json.get('city'),
							state=json.get('state'),
							postal_code=json.get('postalCode'))
		return address