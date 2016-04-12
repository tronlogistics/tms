from app import app
from app import db
from app.models.contact import Contact

class ContactDI():	
	@staticmethod
	def createContactFromForm(form):
		contact = Contact(name=form.contact_name.data,
					phone=form.contact_phone.data,
					email=form.contact_email.data)
		return contact