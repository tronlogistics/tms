from flask.ext.wtf import Form
from wtforms import StringField, FloatField, PasswordField, SelectField, DateField, BooleanField, IntegerField, HiddenField, FormField, FieldList, TextAreaField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Email, Length

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
														('Both', 'Both')], 
														validators = [])
	address1 = StringField("Address 1", validators =[])
	city = StringField("City", validators =[])
	state = StringField("State", validators =[])
	postal_code = StringField("Zip Code", validators =[])
	stop_number = HiddenField("Stop #", validators=[])
	retired = HiddenField("Retired", validators=[])
	arrival_date = DateField("Date", validators=[], format='%m/%d/%Y')
	arrival_Time = StringField("Time", validators=[])
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

class LoadForm(Form):
	name = StringField('Name', validators=[])
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
	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	email = StringField('Email', validators=[Email("Please enter a valid e-mail")])
	phone_number = StringField('Phone', validators=[DataRequired()])
	#phone_area_code = StringField('Area Code', validators=[DataRequired()])
	#phone_prefix = StringField('Prefix', validators=[DataRequired()])
	#phone_line_number = StringField('Line Number', validators=[DataRequired()])

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
	truck = StringField("Truck", validators=[])
	driver = SelectField('Category', choices=[], coerce=int, validators=[])



class LocationStatusForm(Form):
	def __init__(self, *args, **kwargs):
		kwargs['csrf_enabled'] = False
		Form.__init__(self, *args, **kwargs)

	location_id = HiddenField("Location ID", validators=[])
	status = SelectField('Load Status:', choices = [('In Transit', 'In Transit'),
													('Arrived', 'Pending Arrival'),
													('Waiting', 'Pending Arrival'),
													('Loading', 'Arrived'),
													('Loaded/Unloaded', 'Loaded/Unloaded'),
													('Departed', 'Departed')], 
													validators = [])



class StatusForm(Form):
	location_status = FieldList(FormField(LocationStatusForm), validators=[])

