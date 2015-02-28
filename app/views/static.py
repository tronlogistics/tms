from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, mail
from app.forms import LoginForm, RegisterForm, EmailForm, ResetPasswordForm
from app.models import User, Role, Lead
from app.permissions import *
from app.emails import register_account, new_lead, reset_pass, get_serializer
#from app import stripe, stripe_keys

static = Blueprint('static', __name__, url_prefix='')

@lm.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@static.before_request
def before_request():
    g.user = current_user

@static.route('/', methods=['GET', 'POST'])
@static.route('/index', methods=['GET', 'POST'])
@static.route('/home', methods=['GET', 'POST'])
def index():
	form = EmailForm()
	if form.validate_on_submit():
		if not Lead.query.filter_by(email=form.email.data).first():
			lead = Lead(email=form.email.data)
			db.session.add(lead)
			db.session.commit()
			new_lead(lead.email)
		flash("We will notify you of our launch.")
	return render_template('static/coming_soon.html', form=form)

@static.route('/marketing')
def marketing():
	return render_template('static/index.html')

@static.route('/login', methods=['GET', 'POST'])
def login():
	if g.user.is_authenticated():
		return redirect(url_for('loads.all'))
	login_form = LoginForm()
	register_form = RegisterForm()
	forgot_form = EmailForm()

	register_form.account_type.data = 'carrier'
	
	#flash(login_form.is_submitted())
	#flash(login_form.validate_on_submit())
	#flash(login_form.errors)
	#flash(register_form.is_submitted())
	#flash(register_form.validate_on_submit())
	#flash(register_form.errors)
	#flash(forgot_form.is_submitted())
	#flash(forgot_form.validate_on_submit())
	#flash(forgot_form.errors)
	return render_template('static/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)
	if login_form.validate_on_submit():

		user = User.query.filter_by(email=login_form.email.data).first()
		if user is not None:

			if not user.is_confirmed():
				flash("You must confirm your e-mail prior to logging in. To confirm your e-mail, click the activation link provided to %s" % user.email )
				return render_template('static/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)

			if user.check_password(login_form.password.data):
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=True)
				# Tell Flask-Principal the user has logged in
				identity_changed.send(current_app._get_current_object(),
										identity=Identity(user.email))
				return redirect(url_for("loads.all"))
			else:
				flash("Wrong username/password")
				return render_template('static/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)
		else:
			flash("Wrong username/password")
			return render_template('static/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)
		
	if register_form.validate_on_submit():
		user = User(company_name=register_form.company_name.data,
					email=register_form.email.data,
					password=register_form.password.data)
		db.session.add(user)
		role = Role(name=register_form.account_type.data)
		db.session.add(role)
		user.roles.append(role)
		db.session.add(user)
		db.session.commit()
	
		register_account(user)
		flash("A registration e-mail has been sent to %s" % register_form.email.data)
		app.logger.info("User \"%s\" with role \"%s\" created" % (user.email, user.roles[0].name))
	if forgot_form.validate_on_submit():
		user = User.query.filter_by(email=forgot_form.email.data).first()
		app.logger.info("User \"%s\" requested a password reset" % user.email)
		reset_pass(user)
		flash("Password reset instrunctions have been sent to %s" % forgot_form.email.data)
	return render_template('static/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)

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
	register_form = RegisterForm()
	register_form.account_type.data = 'carrier'
	if register_form.validate_on_submit():
		if User.query.filter_by(email=register_form.email.data).first() is not None:
			flash("This e-mail is already registered.")
			return render_template('static/login.html?box-register', login_form=LoginForm(), register_form=register_form, forgot_form=EmailForm(), user=g.user)
		user = User(company_name=register_form.company_name.data,
					email=register_form.email.data,
					password=register_form.password.data)
		db.session.add(user)
		role = Role(name=register_form.account_type.data)
		db.session.add(role)
		user.roles.append(role)
		db.session.add(user)
		db.session.commit()
		
		register_account(user)
		flash("A registration e-mail has been sent to %s" % register_form.email.data)
		app.logger.info("User \"%s\" with role \"%s\" created" % (user.email, user.roles[0].name))
		return redirect(url_for('.login'))
	return render_template('static/register.html', register_form=register_form, user=g.user)

@static.route('/choose_plan', methods=['GET', 'POST'])
def choose_plan():
	return render_template('static/choose_plan.html', key=stripe_keys['publishable_key'], user=g.user)

@static.route('/setup_plan', methods=['POST'])
def charge():
    # Amount in cents
    amount = 0000

    customer = stripe.Customer.create(
        email=g.user.email,
        card=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )
    g.user.customer_id = customer.id
    db.session.add(g.user)
    db.session.commit(g.user)
    return render_template('charge.html', amount=amount)

@static.route('/activate/<activation_slug>')
def activate_user(activation_slug):
    s = get_serializer()
    try:
    	user_id = s.loads(activation_slug)
    	app.logger.info("User %s" % user_id)
    except BadSignature:
    	abort(404)

    user = User.query.get_or_404(user_id)
    user.activate()
    db.session.add(user)
    db.session.commit()
    app.logger.info("User \"%s\" is now activated" % user.email)
    flash('Your account is now activated. Please log in.')
    return redirect(url_for('.login'))

@static.route('/reset/<activation_slug>', methods=['GET', 'POST'])
def reset_password(activation_slug):
	form = ResetPasswordForm()
	flash(form.is_submitted())
	flash(form.validate_on_submit())
	flash(form.errors)
	if form.validate_on_submit():
		g.user.password = form.password.data
		g.user.authenticated = True
		db.session.add(g.user)
		db.session.commit()
		login_user(g.user, remember=True)
		return redirect(url_for('loads.all'))
	else:
		s = get_serializer()
		try:
			user_id = s.loads(activation_slug)
		except BadSignature:
			abort(404)

		user = User.query.get_or_404(user_id)
		login_user(user, remember=True)
		app.logger.info("User \"%s\"'s password is now reset" % user.email)
		flash('Your password has been reset. Please create a new password.')

		return render_template('static/reset_password.html', form=form, user=user)

@static.route('/reset', methods=['POST'])
def change_password():
	form = ResetPasswordForm()
	if form.validate_on_submit():
		g.user.password = form.password.data
		return redirect(url_for('load.all'))

@app.errorhandler(404)
def not_found_error(error):
	app.logger.exception(error)
	return render_template('404.html', user=current_user), 404

@app.errorhandler(500)
def internal_error(error):
	app.logger.exception(error)
	db.session.rollback()
	return render_template('500.html', user=current_user), 500

@identity_loaded.connect_via(app)
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



