from flask import Flask, url_for
from flask.ext import admin, login
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.principal import Principal
from flask.ext.mail import Mail
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.cors import CORS, cross_origin

from flask_restful import Resource, Api
from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

#import stripe


import os

#stripe_keys = {
#	'secret_key': 'sk_test_jFav95nmL7CuiqTq1r3helDT',
#    'publishable_key': 'pk_test_6kN4KpOzRqZww0k55vsbM0Pa'
#}

#stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__, static_url_path="")
app.config.from_object('config')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)

mail = Mail(app)

cors = CORS(app)

principals = Principal(app)

authAPI = HTTPBasicAuth()

api = Api(app)

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

from .views.loads import loads
#from .views.dashboard import dashboard
from .views.fleet import fleet
from .views.drivers import drivers
from .views.trucks import trucks
from .views.static import static
from .authentication.views import auth
from .views.org import org
#
app.register_blueprint(loads)
app.register_blueprint(fleet)
app.register_blueprint(drivers)
app.register_blueprint(trucks)
#app.register_blueprint(dashboard)
app.register_blueprint(static)
app.register_blueprint(auth)
app.register_blueprint(org)

from .views.api import api


#from .controllers.factory import LoadFactory

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

if not app.debug and os.environ.get('HEROKU') is None:
    import logging
    app.logger.setLevel(logging.INFO)
    app.logger.info('TMS startup')

if os.environ.get('HEROKU') is not None:
    import logging
    stream_handler = logging.StreamHandler()
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('TMS startup')

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename = filename)
)

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['f_static'] = (
    lambda filename: url_for('static', filename = filename)
)


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin()


# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated() and login.current_user.is_admin()

#from app import models

#from models import *

from app.models.address import Address
from app.models.associationtables import *
from app.models.bid import Bid
from app.models.bol import BOL
from app.models.company import Company
from app.models.contact import Contact
from app.models.driver import Driver
from app.models.fleet import Fleet
from app.models.lane import Lane
from app.models.load import Load
from app.models.loaddetail import LoadDetail
from app.models.location import Location
from app.models.longlat import LongLat
from app.models.role import Role
from app.models.status import Status
from app.models.truck import Truck
from app.models.user import User



admin = Admin(app, name='Tron Logistics', index_view=MyAdminIndexView())
admin.add_view(MyModelView(Company, db.session))
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(Load, db.session))
admin.add_view(MyModelView(LoadDetail, db.session))
admin.add_view(MyModelView(BOL, db.session))
