from flask.ext.wtf import Form
from wtforms import StringField, FloatField, PasswordField, SelectField, DateField, BooleanField, IntegerField, HiddenField
from wtforms.validators import DataRequired, EqualTo, NumberRange

class LoadForm(Form):
	name = StringField('Name', validators=[])
	origin_address1 = StringField("Address 1", validators =[])
	origin_address2 = StringField("Address 2", validators =[])
	origin_city = StringField("City", validators =[])
	origin_state = StringField("State", validators =[])
	origin_postal_code = StringField("Zip Code", validators =[DataRequired()])
	origin_latitude = FloatField('Latitude', validators=[])
	origin_longitude = FloatField('Longitude', validators=[])
	destination_address1 = StringField("Address 1", validators =[])
	destination_address2 = StringField("Address 2", validators =[])
	destination_city = StringField("City", validators =[])
	destination_state = StringField("State", validators =[])
	destination_postal_code = StringField("Zip Code", validators =[DataRequired()])
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
	trailer_group = SelectField('Trailer Group', choices = [('','<none selected>'),('flat', 'Flat'), ('van', 'Van')], validators = [])
	trailer_type = SelectField('Trailer Type', choices = [('','<none selected>'),('flat', 'Flat'), ('van', 'Van')], validators = [])
	load_type = SelectField('Load Type', choices = [('','<none selected>'),('LTL', 'LTL'), ('TL', 'TL')], validators = [])
	total_miles = IntegerField('Total Miles', validators=[])
	price = FloatField('Total Price', validators=[DataRequired()])
	purchase_order = StringField('Purchase Order', validators =[])
	over_dimensional = BooleanField('Over Dimensional?', validators =[])
	description = StringField('Description', validators=[])
	origin_contact_name = StringField('Name', validators=[])
	origin_contact_email = StringField('Email', validators=[])
	origin_contact_phone = StringField('Phone', validators=[])
	origin_contact_phone_area_code = IntegerField('Area Code', validators=[DataRequired()])
	origin_contact_phone_prefix = IntegerField('Prefix', validators=[DataRequired()])
	origin_contact_phone_line_number = IntegerField('Line Number', validators=[DataRequired()])
	destination_contact_name = StringField('Name', validators=[])
	destination_contact_email = StringField('Email', validators=[])
	destination_contact_phone = StringField('Phone', validators=[])
	destination_contact_phone_area_code = IntegerField('Area Code', validators=[DataRequired()])
	destination_contact_phone_prefix = IntegerField('Prefix', validators=[DataRequired()])
	destination_contact_phone_line_number = IntegerField('Line Number', validators=[DataRequired()])

class TruckForm(Form):
	name = StringField('Name', validators=[DataRequired()])
	trailer_group = SelectField('Trailer Group', choices = [('','<none selected>'),('flat', 'Flat'), ('van', 'Van')], validators = [])
	trailer_type = SelectField('Trailer Type', choices = [('','<none selected>'),('flat', 'Flat'), ('van', 'Van')], validators = [])
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
	email = StringField('Email', validators=[DataRequired()])
	company_name = StringField('Company Name', validators=[DataRequired()])
	password = PasswordField('New Password', [
		DataRequired(),
		EqualTo('confirm', message='Passwords must match')
		])
	confirm = PasswordField('Repeat Password')
	account_type = SelectField('Account Type', choices = [('','<none selected>'),('broker', 'Broker'), ('carrier', 'Carrier')], validators = [DataRequired()])

class BidForm(Form):
	value = FloatField('Bid Amount', validators=[DataRequired()])

class AssignDriverForm(Form):
	truck = IntegerField("Truck", validators=[])
	driver = SelectField('Category', choices=[], coerce=int, validators=[])
