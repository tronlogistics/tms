from flask.ext.wtf import Form
from wtforms import StringField, FloatField, PasswordField, SelectField, DateField, BooleanField, IntegerField, HiddenField, FormField, FieldList, TextAreaField, RadioField
from wtforms.validators import DataRequired, EqualTo, NumberRange, Email, Length

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
	state = SelectField('State', choices = [('','State'),
													('AL', 'Alabama'),
													('AK', 'Alaska'),
													('AZ', 'Arizona'),
													('AR', 'Arkansas'),
													('CA', 'California'),
													('CO', 'Colorado'),
													('CT', 'Connecticut'),
													('DE', 'Delaware'),
													('DC', 'District Of Columbia'),
													('FL', 'Florida'),
													('GA', 'Georgia'),
													('HI', 'Hawaii'),
													('ID', 'Idaho'),
													('IL', 'Illinois'),
													('IN', 'Indiana'),
													('IA', 'Iowa'),
													('KS', 'Kansas'),
													('KY', 'Kentucky'),
													('LA', 'Louisiana'),
													('ME', 'Maine'),
													('MD', 'Maryland'),
													('MA', 'Massachusetts'),
													('MI', 'Michigan'),
													('MN', 'Minnesota'),
													('MS', 'Mississippi'),
													('MO', 'Missouri'),
													('MT', 'Montana'),
													('NE', 'Nebraska'),
													('NV', 'Nevada'),
													('NH', 'New Hampshire'),
													('NJ', 'New Jersey'),
													('NM', 'New Mexico'),
													('NY', 'New York'),
													('NC', 'North Carolina'),
													('ND', 'North Dakota'),
													('OH', 'Ohio'),
													('OK', 'Oklahoma'),
													('OR', 'Oregon'),
													('PA', 'Pennsylvania'),
													('RI', 'Rhode Island'),
													('SC', 'South Carolina'),
													('SD', 'South Dakota'),
													('TN', 'Tennessee'),
													('TX', 'Texas'),
													('UT', 'Utah'),
													('VT', 'Vermont'),
													('VA', 'Virginia'),
													('WA', 'Washington'),
													('WV', 'West Virginia'),
													('WI', 'Wisconsin'),
													('WY', 'Wyoming')], 
													validators = [DataRequired()])
	postal_code = StringField('Zip Code', validators=[])
	email = StringField('Email', validators=[DataRequired()])
	phone_number = StringField('Phone', validators=[DataRequired()])
	password = PasswordField('New Password', [
		DataRequired(),
		EqualTo('confirm', message='Passwords must match')
		])
	confirm = PasswordField('Repeat Password')
	account_type = SelectField('Account Type', choices = [('','Account Type'),('broker', 'Broker/Shiper'), ('carrier', 'Carrier')], validators = [DataRequired()])
	#subscription_tier = SelectField('Account Tier', choices = [('','<none selected>'),('0000', 'BETA Access (Free!)'),('0000', 'Silver ($30/month)'),('0000', 'Gold ($40/month)')], validators = [DataRequired()])
