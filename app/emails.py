from flask.ext.mail import Message
from app import mail, app
from config import ADMINS
from threading import Thread
from flask import current_app, render_template
from .decorators import async
from itsdangerous import URLSafeSerializer, BadSignature

@async
def send_async_email(app, msg):
	try:
		with app.app_context():
			mail.send(msg)
	except Exception, e:
		app.logger.info(e)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def register_account(user):
	app.logger.info("Sending email to %s" % user.email)
	s = get_serializer()

	activation_slug = s.dumps(user.id)
	s = get_serializer()
	try:
		user_id = s.loads(activation_slug)
	except BadSignature:
		abort(404)
	send_email("Register Your Account",
		ADMINS[0],
		[user.email],
		render_template("register_email.txt", 
			user=user, activation_slug=activation_slug),
		render_template("register_email.html", 
			user=user, activation_slug=activation_slug))

def reset_pass(user):
	app.logger.info("Sending email to %s" % user.email)
	s = get_serializer()

	activation_slug = s.dumps(user.id)
	s = get_serializer()
	try:
		user_id = s.loads(activation_slug)
	except BadSignature:
		app.logger.info(error)
		abort(404)
	send_email("Password Reset",
		ADMINS[0],
		[user.email],
		render_template("emails/reset_password.txt", 
			user=user, activation_slug=activation_slug),
		render_template("emails/reset_password.html", 
			user=user, activation_slug=activation_slug))

def new_lead(email):
	app.logger.info("Sending new lead email!")

	send_email("New Lead Notification",
		ADMINS[0],
		[ADMINS[1], ADMINS[2]],
		render_template("emails/new_lead.txt", 
			email=email),
		render_template("emails/new_lead.html", 
			email=email))

def contact_us(form):
	app.logger.info("Sending contact us email!")

	send_email(form.subject.data,
		ADMINS[0],
		[ADMINS[1], ADMINS[2]],
		render_template("emails/contact_us.txt",
			name=form.name.data, 
			email=form.email.data,
			message=form.message.data),
		render_template("emails/contact_us.html",
			name=form.name.data,
			email=form.email.data, 
			message=form.message.data))

def request_demo(form):
	app.logger.info("Sending request demo email!")

	send_email("Demo Requested",
		ADMINS[0],
		[ADMINS[1], ADMINS[2]],
		render_template("emails/request_demo.txt",
			name=form.full_name.data, 
			company=form.company_name.data,
			email=form.email.data,
			phone=form.phone.data,
			number_drivers=form.number_drivers.data,
			number_trucks=form.number_trucks.data),
		render_template("emails/request_demo.html",
			name=form.full_name.data, 
			company=form.company_name.data,
			email=form.email.data,
			phone=form.phone.data,
			number_drivers=form.number_drivers.data,
			number_trucks=form.number_trucks.data))

def ping_driver(driver):
	app.logger.info("Sending driver check-in email!")

	send_email("Please Check In",
		ADMINS[0],
		[driver.email],
		render_template("emails/ping.txt", 
			driver=driver),
		render_template("emails/ping.html", 
			driver=driver))

def bid_accepted(user, load):
	app.logger.info("Sending bid acceptance email!")

	send_email("Bid has been accepted",
		ADMINS[0],
		[user.email],
		render_template("emails/accepted_bid.txt", 
			user=user,
			load=load),
		render_template("emails/accepted_bid.html", 
			user=user,
			load=load))

def get_serializer(secret_key=None):
    if secret_key is None:
        secret_key = app.secret_key
    return URLSafeSerializer(secret_key)

def get_activation_link(user):
    s = get_serializer()
    payload = s.dumps(user.id)
    return url_for('activate_user', payload=payload, _external=True)