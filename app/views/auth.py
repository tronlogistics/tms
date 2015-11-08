from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app, jsonify, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, mail, authAPI, cors
from app.forms import LoginForm, RegisterForm, ForgotForm, ResetPasswordForm, ContactUsForm, EmailForm, DemoForm
from app.models import User, Role, Lead, Address, Company
from app.permissions import *
from app.emails import register_account, new_lead, contact_us, reset_pass, get_serializer, request_demo
from flask.ext.cors import CORS, cross_origin
#from app import stripe, stripe_keys

auth = Blueprint('auth', __name__, url_prefix='/u')

@lm.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@auth.before_request
def before_request():
    g.user = current_user

@auth.route('/login', methods=['GET', 'POST'])
def login():
	if g.user.is_authenticated():
		return redirect(url_for('fleet.view'))
	login_form = LoginForm()
	register_form = RegisterForm()
	forgot_form = ForgotForm()
	
	if login_form.validate_on_submit():

		user = User.query.filter_by(email=login_form.email.data).first()
		if user is not None:
			if not user.is_confirmed():
				flash("You must confirm your e-mail prior to logging in. To confirm your e-mail, click the activation link provided to %s" % user.email )
				return render_template('auth/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)

			if user.check_password(login_form.password.data) and not user.disabled:
				user.authenticated = True
				db.session.add(user)
				db.session.commit()
				login_user(user, remember=False)
				# Tell Flask-Principal the user has logged in
				identity_changed.send(current_app._get_current_object(),
										identity=Identity(user.email))
				if len(user.roles) == 1 and user.roles[0].code == 'driver':
					return redirect(url_for('trucks.check_in'))
				else:
					return redirect(url_for('fleet.view'))
			elif user.disabled:
				flash("Your account has been disabled. Please contact your organization for more information.")
				return render_template('auth/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)
			else:
				flash("Wrong username/password")
				return render_template('auth/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)
		else:
			flash("Wrong username/password")
			return render_template('auth/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)
		
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
	return render_template('auth/login.html', login_form=login_form, register_form=register_form, forgot_form=forgot_form, user=g.user)

@auth.route("/logout", methods=["GET"])
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


@auth.route('/register', methods=['GET', 'POST'])
def register():
	register_form = RegisterForm()
	if register_form.validate_on_submit():
		if User.query.filter_by(email=register_form.email.data).first() is not None:
			flash("This e-mail is already registerd. Please sign in!")
			return redirect(url_for('.login'))
		address = Address(address1=register_form.address.data,
							city=register_form.city.data,
							state=register_form.state.data,
							postal_code=register_form.postal_code.data)
		company = Company(name=register_form.company_name.data,
							address=address,
							company_type=register_form.account_type.data)
		user = User(first_name=register_form.first_name.data,
					last_name=register_form.last_name.data,
					phone=register_form.phone_number.data,
					email=register_form.email.data,
					password=register_form.password.data)
		role = Role.query.filter_by(code='company_admin').first()
		user.roles.append(role)
		company.users.append(user)
		db.session.add(address)
		db.session.add(company)
		db.session.add(user)
		db.session.add(role)
		db.session.commit()


		register_account(user)
		flash("A registration e-mail has been sent to %s" % register_form.email.data)
		app.logger.info("User \"%s\" with role \"%s\" created" % (user.email, user.roles[0].name))
		return redirect(url_for('.login'))
	return redirect(url_for('.login', type='register'))

@auth.route('/choose_plan', methods=['GET', 'POST'])
def choose_plan():
	return render_template('auth/choose_plan.html', key=stripe_keys['publishable_key'], user=g.user)

@auth.route('/setup_plan', methods=['POST'])
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

@auth.route('/activate/<activation_slug>')
def activate_user(activation_slug):
    s = get_serializer()
    app.logger.info("User")
    try:
    	user_id = s.loads(activation_slug)
    	print "%s" % user_id
    	app.logger.info("User %s" % user_id)
    except BadSignature:
    	abort(404)

    user = User.query.get_or_404(user_id)
    user.activate()
    db.session.add(user)
    db.session.commit()
    app.logger.info("User \"%s\" is now activated" % user.email)
    if user.password == "":
    	return redirect(url_for('.set_password', user_id=user_id))
    else:
    	flash('Your account is now activated. Please log in.')
    	return redirect(url_for('.login'))

@auth.route('/reset/<activation_slug>', methods=['GET', 'POST'])
def reset_password(activation_slug):
	form = ResetPasswordForm()

	if form.validate_on_submit():
		g.user.set_password(form.password.data)
		g.user.authenticated = True
		db.session.add(g.user)
		db.session.commit()
		flash("Your password has been updated.")
		return redirect(url_for('fleet.view'))
	else:
		s = get_serializer()
		try:
			user_id = s.loads(activation_slug)
		except BadSignature:
			abort(404)

		user = User.query.get_or_404(user_id)
		login_user(user, remember=False)
		app.logger.info("User \"%s\"'s password is now reset" % user.email)
		flash('Your password has been reset. Please create a new password.')

		return render_template('auth/reset_password.html', form=form, user=user)

@auth.route('/<user_id>/set_password', methods=['GET', 'POST'])
def set_password(user_id):
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.get_or_404(user_id)
		user.set_password(form.password.data)
		user.authenticated = True
		db.session.add(user)
		db.session.commit()
		login_user(user, remember=False)
		flash("Your password has been set.")
		if len(user.roles) == 1 and user.roles[0].code == 'driver':
			return redirect(url_for('trucks.check_in'))
		else:
			return redirect(url_for('fleet.view'))
	else:


		return render_template('auth/create_password.html', form=form, user_id=user_id)

@auth.route('/reset', methods=['POST', 'GET'])
def change_password():
	form = ResetPasswordForm()
	if form.validate_on_submit():
		g.user.password = form.password.data
		return redirect(url_for('load.all'))



#### API ####

@authAPI.verify_password
def verify_password(email_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.check_password(password):
            return False
    g.user = user
    return True


@auth.route('/api/users', methods=['POST'])
def new_user():
	first_name = request.json.get('first_name')
	last_name = request.json.get('last_name')
	phone_number = request.json.get('phone_number')
	company_name = "%s %s" % (first_name, last_name)
	role = Role.query.filter_by(code='owner_operator').first()
	address = request.json.get('address')
	city = request.json.get('city')
	state = request.json.get('state')
	postal_code = request.json.get('postal_code')
	email = request.json.get('email')
	password = request.json.get('password')
	if email is None or password is None:
		abort(400)    # missing arguments
	if User.query.filter_by(email=email).first() is not None:
		abort(400)    # existing user
	address = Address(address1=address,
						city=city,
						state=state,
						postal_code=postal_code)
	company = Company(name=company_name,
						address=address,
						company_type="Owner Operator")
	user = User(first_name=first_name,
				last_name=last_name,
				phone=phone_number,
				email=email,
				password=password)
	user.roles.append(role)
	company.users.append(user)
	user.activated = True
	db.session.add(address)
	db.session.add(company)
	db.session.add(user)
	db.session.commit()
	login_user(user, remember=True)
	identity_changed.send(current_app._get_current_object(),
										identity=Identity(user.email))
	token = g.user.generate_auth_token(600)
	jsonify({'token': token.decode('ascii'), 'duration': 600})
	return (jsonify({'token': token.decode('ascii'), 'duration': 600}), 201)

@auth.route('/api/login', methods=['POST'])
def api_login_user():
	print "--------- %s" % request.json
	email = request.json.get('email')
	password = request.json.get('password')
	if email is None or password is None:
		abort(400)    # missing arguments
	user = User.query.filter_by(email=email).first()
	if User.query.filter_by(email=email).first() is None:
		abort(400)    # no existing user
	login_user(user, remember=True)
	identity_changed.send(current_app._get_current_object(),
										identity=Identity(user.email))
	return (jsonify({'email': user.email}), 201,
		{'Location': url_for('.get_user', id=user.id, _external=True)})

@auth.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@auth.route('/api/loads')
@cross_origin()
def get_load():
    load = User.query.all()[0]
    
    return jsonify({'test': 'test'})


@auth.route('/api/token')
@authAPI.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@auth.route('/api/resource')
@authAPI.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


#############


@app.errorhandler(401)
def no_access_error(error):
	flash("You must sign in to view this page")
	return redirect(url_for('auth.login'))

@app.errorhandler(403)
def forbidden_error(error):
	app.logger.info(error)
	return render_template('static/404.html'), 403

@app.errorhandler(404)
def not_found_error(error):
	app.logger.info(error)
	return render_template('static/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
	print "%s" % error
	app.logger.info(error)
	db.session.rollback()
	return render_template('static/500.html', error=error), 500
