from flask import Flask, url_for
import os

app = Flask(__name__)

from .views.load import load
#from .views.dashboard import dashboard
#from .views.carrier import carrier
#from .views.static import static
app.register_blueprint(load)
#tronms.register_blueprint(carrier)
#tronms.register_blueprint(dashboard)
#tronms.register_blueprint(static)

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename = filename)
)

from app import views, models
