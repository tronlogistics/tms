from flask.ext.wtf import Form
from wtforms import StringField, FloatField, PasswordField, SelectField, DateField, BooleanField, IntegerField, HiddenField, FormField, FieldList, TextAreaField, RadioField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Email, Length

class BOLForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)

	bol_number = StringField('BOL #', validators=[DataRequired()])
	weight = StringField('Weight', validators=[])
	dim_length = StringField('Length', validators=[])
	dim_width = StringField('Width', validators=[])
	dim_height = StringField('Height', validators=[])
	dim_height_type = SelectField('Height Type', coerce=str, choices = [('',''),
															('Inches', 'in.'), 
															('Centimeters', 'cm.')], 
															validators = [])
	dim_length_type = SelectField('Length Type', coerce=str, choices = [('',''),
															('Inches', 'in.'), 
															('Centimeters', 'cm.')], 
															validators = [])
	dim_width_type = SelectField('Width Type', coerce=str, choices = [('',''),
															('Inches', 'in.'), 
															('Centimeters', 'cm.')], 
															validators = [])
	number_units = StringField('Number of Unitys', validators=[])
	commodity_type = StringField('Commodity Type', validators=[])

class EmailForm(Form):
	new_email = StringField('Lead Email', validators=[Email("Please enter a valid e-mail")])

class ForgotForm(Form):
	email = StringField('Lead Email', validators=[Email("Please enter a valid e-mail")])

class StopNumberForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)

	location_id = HiddenField("Location", validators=[])
	stop_number = HiddenField("Stop #", validators=[])

class RouteForm(Form):
	locations = FieldList(FormField(StopNumberForm), validators=[])
	
class ContactForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)

	company_name = StringField('Name', validators=[])
	phone = StringField('Phone', validators=[])
	email = StringField('Email', validators=[])

class DemoForm(Form):
	full_name = StringField('Name', validators=[DataRequired()])
	company_name = StringField('Name', validators=[DataRequired()])
	phone = StringField('Phone Number', validators=[DataRequired()])
	email = StringField('Email', validators=[Email("Please enter a valid e-mail")])
	number_trucks = StringField('# of Trucks', validators=[DataRequired()])
	number_drivers = StringField('# of Drivers', validators=[DataRequired()])

class ContactUsForm(Form):
	name = StringField('Name', validators=[DataRequired()])
	email = StringField('Email', validators=[Email("Please enter a valid e-mail")])
	subject = StringField('Subject', validators=[DataRequired()])
	message = TextAreaField('Message', validators=[DataRequired()])

class LaneLocationForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)

	stop_type = SelectField('Location Type', coerce=str, choices = [('','<none selected>'),
														('Pickup', 'Pickup'), 
														('Drop Off', 'Drop Off'), 
														('Pick/Drop', 'Pick/Drop')], 
														validators = [])
	address1 = StringField("Address 1", validators =[])
	city = StringField("City", validators =[])
	state = StringField("State", validators =[])
	postal_code = StringField("Zip Code", validators =[])
	stop_number = HiddenField("Stop #", validators=[])
	retired = HiddenField("Retired", validators=[])
	arrival_date = DateField("Date", validators=[], format='%m/%d/%Y')
	arrival_Time = StringField("Time", validators=[])
	notes = TextAreaField('Description', validators=[])
	pickup_weight = StringField("Pickup Weight", validators=[])
	pickup_notes = TextAreaField('Description', validators=[])
	delivery_weight = StringField("Delivery Weight", validators=[])
	delivery_notes = TextAreaField('Description', validators=[])
	contact_name = StringField('Name', validators=[])
	contact_email = StringField('Email', validators=[])
	contact_phone = StringField('Phone', validators=[])
	contact_phone_area_code = StringField('Area Code', validators=[])
	contact_phone_prefix = StringField('Prefix', validators=[])
	contact_phone_line_number = StringField('Line Number', validators=[])
	BOLs = FieldList(FormField(BOLForm), validators=[])

class LoadForm(Form):
	name = StringField('Name', validators=[DataRequired()])
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
															validators = [DataRequired()])
	load_type = SelectField('Load Type', choices = [('','<none selected>'),('LTL', 'LTL'), ('TL', 'TL')], validators = [DataRequired()])
	total_miles = StringField('Total Miles', validators=[DataRequired()])
	price = StringField('Total Price', validators=[DataRequired()])
	purchase_order = StringField('Purchase Order', validators =[])
	description = TextAreaField('Description', validators=[])
	broker = FormField(ContactForm)
	shipper = FormField(ContactForm)
	locations = FieldList(FormField(StopNumberForm), validators=[])

class PostLoadForm(Form):
	name = StringField('Name', validators=[DataRequired()])
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
															validators = [DataRequired()])
	load_type = SelectField('Load Type', choices = [('','<none selected>'),('LTL', 'LTL'), ('TL', 'TL')], validators = [DataRequired()])
	total_miles = StringField('Total Miles', validators=[DataRequired()])
	max_weight = StringField('Max Weight', validators =[DataRequired()])
	max_height = StringField('Max Height', validators =[DataRequired()])
	max_length = StringField('Max Length', validators =[DataRequired()])
	max_width = StringField('Max Width', validators =[DataRequired()])
	max_height_type = SelectField('Height Type', choices = [('','<none selected>'),
															('Inches', 'in.'), 
															('Centimeters', 'cm.')], 
															validators = [DataRequired()])
	max_length_type = SelectField('Length Type', choices = [('','<none selected>'),
															('Inches', 'in.'), 
															('Centimeters', 'cm.')], 
															validators = [DataRequired()])
	max_width_type = SelectField('Width Type', choices = [('','<none selected>'),
															('Inches', 'in.'), 
															('Centimeters', 'cm.')], 
															validators = [DataRequired()])
	over_dimensional = BooleanField('Over Dimenensional', validators=[])
	locations = FieldList(FormField(LaneLocationForm), validators=[])

class AcceptBidForm(Form):
	locations = FieldList(FormField(LaneLocationForm), validators=[])

class TruckForm(Form):
	name = StringField('Name', validators=[DataRequired()])
	trailer_type = SelectField('Trailer Type', choices = [('','<none selected>'),
															('Auto Carrier', 'Auto Carrier'), 
															('Conestoga', 'Conestoga'),
															('Container', 'Container'),
															('Double Drop', 'Double Drop'),
															('Flatbed', 'Flatbed'),
															('hotshot', 'Hotshot'),
															('Lowboy', 'Lowboy'),
															('Moving Van', 'Moving Van'),
															('Power Only', 'Power Only'),
															('Reefer', 'Reefer'),
															('RGN', 'RGN'),
															('Step Deck', 'Step Deck'),
															('Tanker', 'Tanker'),
															('Van', 'Van'),], 
															validators = [DataRequired()])
	max_weight = StringField("Max Weight", validators =[])
	dim_length = StringField("Length", validators =[])
	dim_height = StringField("Height", validators =[])
	dim_width = StringField("Width", validators =[])
	locations = FieldList(FormField(StopNumberForm), validators=[])

class DriverForm(Form):
	first_name = StringField('Name', validators=[DataRequired()])
	last_name = StringField('Name', validators=[DataRequired()])
	email = StringField('Email', validators=[Email("Please enter a valid e-mail"),DataRequired()])
	phone_number = StringField('Phone', validators=[DataRequired()])
	driver_type = SelectField('Driver Type', choices = [('','<none selected>'),
															('Company Driver', 'Company Driver'), 
															('Owner Operator', 'Owner Operator')], 
															validators = [DataRequired()])
	has_account = BooleanField('Has Account', validators=[])

class LoginForm(Form):
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])

class ResetPasswordForm(Form):
	password = PasswordField('New Password', [
		DataRequired(),
		EqualTo('confirm', message='Passwords must match')
		])
	confirm = PasswordField('Repeat Password')

class RegisterForm(Form):
	company_name = StringField('Company Name', validators=[DataRequired()])
	first_name = StringField('Name', validators=[DataRequired()])
	last_name = StringField('Name', validators=[DataRequired()])
	address = StringField('Address', validators=[])
	city = StringField('City', validators=[])
	state = StringField('State', validators=[])
	postal_code = StringField('Zip Code', validators=[])
	email = StringField('Email', validators=[DataRequired()])
	phone_number = StringField('Phone', validators=[DataRequired()])
	password = PasswordField('New Password', [
		DataRequired(),
		EqualTo('confirm', message='Passwords must match')
		])
	confirm = PasswordField('Repeat Password')
	account_type = SelectField('Account Type', choices = [('','<none selected>'),('broker', 'Broker/Shiper'), ('carrier', 'Carrier')], validators = [DataRequired()])
	#subscription_tier = SelectField('Account Tier', choices = [('','<none selected>'),('0000', 'BETA Access (Free!)'),('0000', 'Silver ($30/month)'),('0000', 'Gold ($40/month)')], validators = [DataRequired()])

class BidForm(Form):
	value = FloatField('Bid Amount', validators=[DataRequired()])

class AssignDriverForm(Form):
	truck = StringField("Truck", validators=[])
	driver = SelectField('Category', choices=[], coerce=int, validators=[])



class LocationStatusForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)

	location_id = HiddenField("Location ID", validators=[])
	status = SelectField('Load Status:', choices = [('En Route', 'En Route'),
													('Arrived', 'Arrived'),
													('Loaded/Unloaded', 'Loaded/Unloaded'),
													('Departed', 'Departed')], 
													validators = [])



class StatusForm(Form):
	location_status = FieldList(FormField(LocationStatusForm), validators=[])

class CreateUserForm(Form):
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('First Name', validators=[DataRequired()])
	email = StringField('Email', validators=[Email("Please enter a valid e-mail")])
	phone_number = StringField('Phone Number', validators=[DataRequired()])
	role = SelectField('Location Type', coerce=str, choices = [('','<none selected>'),
														('driver', 'Driver'), 
														('company_admin', 'Company Admin')], 
														validators = [DataRequired()])




