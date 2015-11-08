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
#import stripe


import os

#stripe_keys = {
#	'secret_key': 'sk_test_jFav95nmL7CuiqTq1r3helDT',
#    'publishable_key': 'pk_test_6kN4KpOzRqZww0k55vsbM0Pa'
#}

#stripe.api_key = stripe_keys['secret_key']

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)

mail = Mail(app)

cors = CORS(app)

principals = Principal(app)

authAPI = HTTPBasicAuth()

from .views.loads import loads
#from .views.dashboard import dashboard
from .views.fleet import fleet
from .views.drivers import drivers
from .views.trucks import trucks
from .views.static import static
from .views.auth import auth
from .views.org import org
app.register_blueprint(loads)
app.register_blueprint(fleet)
app.register_blueprint(drivers)
app.register_blueprint(trucks)
#app.register_blueprint(dashboard)
app.register_blueprint(static)
app.register_blueprint(auth)
app.register_blueprint(org)


#from .controllers.factory import LoadFactory

from config import basedir, ADMINS, MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD

if not app.debug and os.environ.get('HEROKU') is None:
    import logging
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler('tmp/tms.log', 'a', 1 * 1024 * 1024, 10)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(file_handler)
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

from models import *
admin = Admin(app, name='Tron Logistics', index_view=MyAdminIndexView())
admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Role, db.session))
admin.add_view(MyModelView(Load, db.session))
admin.add_view(MyModelView(LoadDetail, db.session))
admin.add_view(MyModelView(BOL, db.session))

