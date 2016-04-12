from app import app
from app import db
from app.repositories.addressrepository import AddressDI
from app.models.company import Company

class CompanyDI():

	@staticmethod
	def createCompanyFromForm(form):
		address = AddressDI.createAddressFromForm(form)
		company = Company(mco=form.mco.data, 
							name=form.company_name.data,
							address=address,
							company_type=form.account_type.data)
		return company

	@staticmethod
	def createCompanyFromJSON(json):
		roleCode = json.get('type')
		company = None
		address = AddressDI.createAddressFromJSON(json)
		if roleCode == "owner_operator":
			company = Company(mco=json.get('mco'), 
							name=json.get('companyName'),
							address=address,
							company_type="Owner Operator")
		elif roleCode == "broker" or roleCode == "shipper":
			company = Company(mco=json.get('mco'), 
							name=json.get('companyName'),
							address=address,
							company_type="Shipper/Broker")
		else:
			company = Company(mco=json.get('mco'), 
							name=json.get('companyName'),
							address=address,
							company_type="Carrier")
		return company

	@staticmethod
	def findCompanyByMCO(mco):
		return Company.query.filter_by(mco=mco).first()
