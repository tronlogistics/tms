from flask import Blueprint, render_template, url_for, redirect, request, flash, session, abort, g, jsonify
from flask.ext.login import current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app
from app.forms import DriverForm, TruckForm, AssignDriverForm
from app.models import Load, Driver, Truck, LongLat
from app.permissions import *
from app.emails import ping_driver, get_serializer

trucks = Blueprint('trucks', __name__, url_prefix='/trucks')

@lm.user_loader
def user_loader(user_id):
	return User.query.get(user_id)

@trucks.before_request
def before_request():
	g.user = current_user


#############################
#							#
#							#
#	   TRUCK - CRUD			#
#							#
#							#
#############################

@trucks.route('/all', methods=['GET', 'POST'])
@login_required
def all():
	return render_template("carrier/truck/all.html", 
							trucks=g.user.fleet.trucks, 
							user=g.user,
							active="Trucks")

@trucks.route('/create', methods=['GET', 'POST'])
@login_required
def create():
	if g.user.is_carrier():
		form = TruckForm()
		if form.validate_on_submit():
			truck = Truck(name=form.name.data, 
						trailer_type=form.trailer_type.data,
						max_weight=form.max_weight.data,
						dim_length=form.dim_length.data,
						dim_height=form.dim_height.data,
						dim_width=form.dim_width.data,
						is_available=True,
						tracker = [])
			db.session.add(truck)
			g.user.fleet.trucks.append(truck)
			db.session.add(g.user)
			db.session.commit()
			return redirect(url_for('.view', truck_id=truck.id))
		return render_template('carrier/truck/create.html',
    							title="Create Truck",
    							form=form,
    							active="Trucks",
    							user=g.user)
	abort(403)



@trucks.route('/edit/<truck_id>', methods=['GET', 'POST'])
@login_required
def edit(truck_id):
	permission = EditTruckPermission(truck_id)
	if permission.can():
		form = TruckForm()
		truck = Truck.query.get(int(truck_id))
		if form.validate_on_submit():
			truck.name = form.name.data
			#carrier.latitude = form.latitude.data
			#carrier.longitude = form.longitude.data
			db.session.add(truck)
			db.session.commit()
			return redirect(url_for('.all'))
		else:
			#form.latitude.data = carrier.latitude
			#form.longitude.data = carrier.longitude
			form.name.data = truck.name
			form.trailer_type.data = truck.trailer_type
			form.max_weight.data = truck.max_weight
			form.dim_length.data = truck.dim_length
			form.dim_height.data = truck.dim_height
			form.dim_width.data = truck.dim_width
		return render_template('carrier/truck/edit.html', 
								title="Edit Truck", 
								form=form, 
								truck=truck, 
								active="Trucks",
								user=g.user)
	abort(403)

@trucks.route('/view/<truck_id>', methods=['GET', 'POST'])
@login_required
def view(truck_id):
	permission = ViewTruckPermission(truck_id)
	if permission.can():
		form = AssignDriverForm()
		categories = [('0', '<none selected>')] + [(driver.id, driver.get_full_name()) for driver in filter((lambda driver: driver.truck is None), g.user.fleet.drivers)]# + [('-1', 'Create New Driver...')]
		form.driver.choices = categories
		truck = Truck.query.get(int(truck_id))
		return render_template('carrier/truck/view.html', 
								title="View Truck", 
								form=form, 
								truck=truck, 
								user=g.user)
	abort(403)



@trucks.route('/delete/<truck_id>', methods=['GET', 'POST'])
@login_required
def delete(truck_id):
	permission = DeleteTruckPermission(truck_id)
	if permission.can():
		truck = Truck.query.get(int(truck_id))
		db.session.delete(truck)
		db.session.commit()
		return redirect(url_for('.all'))
	abort(403)

###########################################

@trucks.route('/ping/<truck_id>', methods=['GET', 'POST'])
def ping(truck_id):
	truck = Truck.query.get(int(truck_id))
	ping_driver(truck.driver)
	return jsonify({'message': 'Pinged ' + truck.driver.get_full_name()})

@trucks.route('/checkin/<activation_slug>', methods=['GET', 'POST'])
def check_in(activation_slug):
	s = get_serializer()
	try:
		truck_id = s.loads(activation_slug)
		app.logger.info("User %s" % user_id)
	except BadSignature:
		abort(404)

	truck = Truck.query.get_or_404(truck_id)
	return render_template('carrier/truck/checkin.html', truck=truck)

@trucks.route('/storelocation/<truck_id>', methods=['POST'])
def store_location(truck_id):
	truck = Truck.query.get(int(truck_id))
	longlat = LongLat(latitude=request.form['lat'],
						longitude=request.form['long'])
	truck.tracker.append(longlat)
	for load in filter((lambda l: l.status != "Load Complete"), truck.driver.loads):
		load.tracker.append(longlat)
	if truck.tracker.count() > 10: 
		truck.tracker.pop()
	db.session.add(truck)
	db.session.add(load)
	db.session.commit()
	return jsonify({'message': 'Thank you for checking in!'})

##########
#  MISC  #
##########
@app.errorhandler(404)
def not_found_error(error):
	app.logger.exception(error)
	return render_template('404.html', user=g.user), 404

@app.errorhandler(500)
def internal_error(error):
	print error
	app.logger.exception(error)
	db.session.rollback()
	return render_template('500.html', user=g.user), 500

@identity_changed.connect
def on_identity_changed(sender, identity):
	# Set the identity user object
	identity.user = g.user
	# Add the UserNeed to the identity
	if hasattr(current_user, 'id'):
		identity.provides.add(UserNeed(current_user.id))

	# Assuming the User model has a list of roles, update the
	# identity with the roles that the user provides
	if hasattr(current_user, 'roles'):
		for role in current_user.roles:
			identity.provides.add(RoleNeed(role.name))

	# Assuming the User model has a list of posts the user
	# has authored, add the needs to the identity
	if hasattr(current_user, 'brokered_loads'):
		for load in current_user.brokered_loads:
			identity.provides.add(EditLoadNeed(unicode(load.id)))
			identity.provides.add(DeleteLoadNeed(unicode(load.id)))
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			identity.provides.add(AssignLoadNeed(unicode(load.id)))

	if hasattr(current_user, 'assigned_loads'):
		for load in current_user.assigned_loads:
			identity.provides.add(ViewLoadNeed(unicode(load.id)))
			identity.provides.add(AssignLoadNeed(unicode(load.id)))

	if hasattr(current_user, 'fleet'):
		for truck in current_user.fleet.trucks:
			identity.provides.add(EditTruckNeed(unicode(truck.id)))
			identity.provides.add(DeleteTruckNeed(unicode(truck.id)))
			identity.provides.add(ViewTruckNeed(unicode(truck.id)))

		for driver in current_user.fleet.drivers:
			identity.provides.add(EditDriverNeed(unicode(driver.id)))
			identity.provides.add(DeleteDriverNeed(unicode(driver.id)))
			identity.provides.add(ViewDriverNeed(unicode(driver.id)))

	if hasattr(current_user, 'offered_bids'):
		for bid in current_user.offered_bids:
			identity.provides.add(ViewLoadNeed(unicode(bid.load.id)))
			identity.provides.add(AssignLoadNeed(unicode(bid.load.id)))
