from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
import os

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

lm = LoginManager()
lm.init_app(app)

from .views.load import load
#from .views.dashboard import dashboard
#from .views.carrier import carrier
from .views.static import static
app.register_blueprint(load)
#app.register_blueprint(carrier)
#app.register_blueprint(dashboard)
app.register_blueprint(static)

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename = filename)
)

from app import views, models
