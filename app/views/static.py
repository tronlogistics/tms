from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from tronms import db, lm, bcrypt, tronms
from tronms.forms import LoginForm, RegisterForm
from tronms.models import User, Role, Fleet
from tronms.permissions import *



static = Blueprint('static', __name__, url_prefix='')

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@static.before_request
def before_request():
    g.user = current_user

@static.route('/')
def index():
	form = LoginForm()
	return render_template('static/index.html')

@static.route('/login', methods=['GET', 'POST'])
def login():
	if g.user.is_authenticated():
		return redirect(url_for('load.all'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.get(form.email.data)
		#user = User.query.filter_by(email=form.email.data).first()
		
		#return render_template('static/login.html', form=form)
		if user is not None:
			if bcrypt.check_password_hash(user.password, form.password.data):

				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=True)

				# Tell Flask-Principal the user has logged in
				identity_changed.send(current_app._get_current_object(),
										identity=Identity(user.email))
				return redirect(url_for("load.all"))
	return render_template('static/login.html', form=form, user=g.user)

@static.route("/logout", methods=["GET"])
@login_required
def logout():
    #Logout the current user.
    user = g.user
    user.authenticated = False
    #flash('Logging in - %s' % g.user.is_authenticated())
    db.session.add(user)
    db.session.commit()
    logout_user()
    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
    	session.pop(key, None)

	# Tell Flask-Principal the user is anonymous
	identity_changed.send(current_app._get_current_object(),
							identity=AnonymousIdentity())

    return redirect(url_for('.login'))


@static.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(company_name=form.company_name.data,
					email=form.email.data,
					password=form.password.data)
		db.session.add(user)
		role = Role(name=form.account_type.data)
		db.session.add(role)
		user.roles.append(role)
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('.login'))
	return render_template('static/register.html', form=form, user=g.user)

@identity_loaded.connect_via(tronms)
def on_identity_loaded(sender, identity):
	# Set the identity user object
	identity.user = current_user

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
			if load.assigned_driver is not None:
				identity.provides.add(ViewDriverNeed(unicode(load.assigned_driver.id)))

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


