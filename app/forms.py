from flask.ext.wtf import Form
from wtforms import StringField, FloatField, PasswordField, SelectField, DateField, BooleanField, IntegerField, HiddenField, FormField, FieldList, TextAreaField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Email

class EmailForm(Form):
	email = StringField('Email', validators=[Email("Please enter a valid e-mail")])

class LocationForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)


	address1 = StringField("Address 1", validators =[])
	address2 = StringField("Address 2", validators =[])
	city = StringField("City", validators =[])
	state = StringField("State", validators =[])
	postal_code = StringField("Zip Code", validators =[])
	stop_number = StringField("Stop #", validators=[])
	contact_name = StringField('Name', validators=[])
	contact_email = StringField('Email', validators=[])
	contact_phone = StringField('Phone', validators=[])
	contact_phone_area_code = IntegerField('Area Code', validators=[])
	contact_phone_prefix = IntegerField('Prefix', validators=[])
	contact_phone_line_number = IntegerField('Line Number', validators=[])

class LoadForm(Form):
	name = StringField('Name', validators=[])
	origin_address1 = StringField("Address 1", validators =[])
	origin_address2 = StringField("Address 2", validators =[])
	origin_city = StringField("City", validators =[])
	origin_state = StringField("State", validators =[])
	origin_postal_code = StringField("Zip Code", validators =[])
	origin_latitude = FloatField('Latitude', validators=[])
	origin_longitude = FloatField('Longitude', validators=[])
	destination_address1 = StringField("Address 1", validators =[])
	destination_address2 = StringField("Address 2", validators =[])
	destination_city = StringField("City", validators =[])
	destination_state = StringField("State", validators =[])
	destination_postal_code = StringField("Zip Code", validators =[])
	destination_latitude = FloatField('Latitude', validators=[])
	destination_longitude = FloatField('Longitude', validators=[])
	weight = IntegerField("Weight", validators =[])
	dim_length = IntegerField("Length", validators =[])
	dim_height = IntegerField("Height", validators =[])
	dim_width = IntegerField("Width", validators =[])
	number_pieces = IntegerField("Number of Pieces", validators =[])
	comments = StringField("Comments", validators =[])
	pickup_date = DateField("Pickup Date", validators = [], format='%m/%d/%Y')
	delivery_date = DateField('Delivery Date', validators = [], format='%m/%d/%Y')
	trailer_type = SelectField('Trailer Type', choices = [('','<none selected>'),
															('Auto Carrier', 'Auto Carrier'), 
															('Conestoga', 'Conestoga'),
															('Container', 'Container'),
															('Double Drop', 'Double Drop'),
															('Flatbed', 'Flatbed'),
															('Hotshot', 'Hotshot'),
															('Lowboy', 'Lowboy'),
															('Moving Van', 'Moving Van'),
															('Power Only', 'Power Only'),
															('Reefer', 'Reefer'),
															('RGN', 'RGN'),
															('Step Deck', 'Step Deck'),
															('Tanker', 'Tanker'),
															('Van', 'Van'),], 
															validators = [])
	load_type = SelectField('Load Type', choices = [('','<none selected>'),('LTL', 'LTL'), ('TL', 'TL')], validators = [])
	total_miles = IntegerField('Total Miles', validators=[])
	price = FloatField('Total Price', validators=[DataRequired()])
	purchase_order = StringField('Purchase Order', validators =[])
	over_dimensional = BooleanField('Over Dimensional?', validators =[])
	description = TextAreaField('Description', validators=[])
	origin_contact_name = StringField('Name', validators=[])
	origin_contact_email = StringField('Email', validators=[])
	origin_contact_phone = StringField('Phone', validators=[])
	origin_contact_phone_area_code = IntegerField('Area Code', validators=[])
	origin_contact_phone_prefix = IntegerField('Prefix', validators=[])
	origin_contact_phone_line_number = IntegerField('Line Number', validators=[])
	destination_contact_name = StringField('Name', validators=[])
	destination_contact_email = StringField('Email', validators=[])
	destination_contact_phone = StringField('Phone', validators=[])
	destination_contact_phone_area_code = IntegerField('Area Code', validators=[])
	destination_contact_phone_prefix = IntegerField('Prefix', validators=[])
	destination_contact_phone_line_number = IntegerField('Line Number', validators=[])
	#location = FormField(LocationForm)
	locations = FieldList(FormField(LocationForm))



class TruckForm(Form):
	name = StringField('Name', validators=[DataRequired()])
	trailer_type = SelectField('Trailer Type', choices = [('','<none selected>'),
															('auto_carrier', 'Auto Carrier'), 
															('conestoga', 'Conestoga'),
															('container', 'Container'),
															('double_drop', 'Double Drop'),
															('flatbed', 'Flatbed'),
															('hotshot', 'Hotshot'),
															('lowboy', 'Lowboy'),
															('moving_van', 'Moving Van'),
															('power_only', 'Power Only'),
															('reefer', 'Reefer'),
															('rgn', 'RGN'),
															('step_deck', 'Step Deck'),
															('tanker', 'Tanker'),
															('van', 'Van'),], 
															validators = [])
	max_weight = IntegerField("Max Weight", validators =[])
	dim_length = IntegerField("Length", validators =[])
	dim_height = IntegerField("Height", validators =[])
	dim_width = IntegerField("Width", validators =[])

class DriverForm(Form):
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	phone_area_code = IntegerField('Area Code', validators=[DataRequired()])
	phone_prefix = IntegerField('Prefix', validators=[DataRequired()])
	phone_line_number = IntegerField('Line Number', validators=[DataRequired()])

class LoginForm(Form):
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])

class RegisterForm(Form):
	company_name = StringField('Company Name', validators=[DataRequired()])
	name = StringField('Name', validators=[DataRequired()])
	address = StringField('Address', validators=[])
	city = StringField('City', validators=[])
	state = StringField('State', validators=[])
	postal_code = StringField('Zip Code', validators=[])
	email = StringField('Email', validators=[DataRequired()])
	password = PasswordField('New Password', [
		DataRequired(),
		EqualTo('confirm', message='Passwords must match')
		])
	confirm = PasswordField('Repeat Password')
	account_type = SelectField('Account Type', choices = [('','<none selected>'),('broker', 'Broker'), ('carrier', 'Carrier')], validators = [DataRequired()])
	#subscription_tier = SelectField('Account Tier', choices = [('','<none selected>'),('0000', 'BETA Access (Free!)'),('0000', 'Silver ($30/month)'),('0000', 'Gold ($40/month)')], validators = [DataRequired()])

class BidForm(Form):
	value = FloatField('Bid Amount', validators=[DataRequired()])

class AssignDriverForm(Form):
	truck = IntegerField("Truck", validators=[])
	driver = SelectField('Category', choices=[], coerce=int, validators=[])

class StatusForm(Form):
	status = SelectField('Load Status:', choices = [#('Pending Truck Assignment', 'Pending Truck Assignment'),
													('Truck Assigned', 'Truck Assigned'),
													('In Transit to Pickup', 'In Transit to Pickup'),
													('Truck at Origin Location', 'Truck at Origin Location'),
													('In Transit', 'In Transit'), 
													('Truck at Destination', 'Truck at Destination'), 
													('Load Complete', 'Load Completed')], 
													validators = [DataRequired()])


