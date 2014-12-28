from flask import Blueprint, render_template, url_for, redirect, request, flash, session
from flask.ext.login import current_user, login_required
from tronms import db
from tronms.models import *

dashboard = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard.route('/')
def index():
	loads = Load.query.all()
	return render_template('dashboard/index.html', 
							pending_loads=filter((lambda load: not load.is_assigned), loads), 
							assigned_loads=filter((lambda load: load.is_assigned), loads))
