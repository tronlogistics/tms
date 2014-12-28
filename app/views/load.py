from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, abort
#from flask.ext.login import current_user, login_required
#from flask.ext.principal import identity_changed, Identity, RoleNeed
#from geopy import geocoders 
#from geopy.geocoders import Nominatim
#from app import db, lm, tronms, SQLAlchemy
#from app.forms import LoadForm, BidForm
#from app.models import Load, LoadDetail, Lane, Location, Truck, User, Bid, Driver
#from app.permissions import *
#from sqlalchemy import desc

load = Blueprint('load', __name__, url_prefix='/load')

@load.route("/")
def all():
	#loads = Load.query.all()
	#return render_template('load/all.html', loads=loads)
	
	#TODO: if user is a broker - return all loads the broker created
	#return render_template('load/all.html', loads=g.user.loads)
	#TODO: if the user is a carrier - return all loads that have one of their
	#fleet memebers assigned
	#if g.user.is_carrier():
	#	loads = []
	#	for load in Load.query.all():
	#		if load.status == "Assigned" and load.carrier == g.user:
	#			loads.append(load)
	#		else:
	#			for bid in load.bids:
	#				if bid.offered_to == g.user:
	#					loads.append(load)
	#	loads.append(g.user.brokered_loads)
	#	return render_template('load/all.html', loads=loads)
	#else:
	
	return render_template('load/all.html')#, loads=g.user.brokered_loads, user=g.user)