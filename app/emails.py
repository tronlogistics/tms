from flask.ext.mail import Message
from app import mail, app
from config import ADMINS
from threading import Thread
from flask import current_app, render_template
from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(app, msg)

def register_account(user):
	app.logger.info("Sending email to %s" % [ADMINS[1]])
	send_email("Register Your Account",
		ADMINS[0],
		[user.email],
		render_template("register_email.txt", 
			user=user),
		render_template("register_email.html", 
			user=user))