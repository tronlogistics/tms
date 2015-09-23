from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app, abort
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.principal import identity_loaded, Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed
from app import db, lm, app, mail
from app.forms import CreateUserForm
from app.models import User, Role, Lead, Address, Company
from app.permissions import *
from app.emails import register_account, new_lead, contact_us, reset_pass, get_serializer, request_demo
#from app import stripe, stripe_keys

org = Blueprint('org', __name__, url_prefix='/org')

@lm.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@org.before_request
def before_request():
    g.user = current_user

@org.route('/', methods=['GET', 'POST'])
def view():
	permission = ViewCompanyPermission(g.user.company.id)
	if permission.can():
		return render_template('org/view.html', active="Company", title="My Organization", company=g.user.company)
	abort(403)  # HTTP Forbidden

@org.route('/create_user', methods=['GET', 'POST'])
def create_user():
	form = CreateUserForm()
	if form.validate_on_submit():
		role = Role(name=form.role.data)
		user = User(name=register_form.company_name.data,
					email=register_form.email.data,
					roles=[role])
		user.company = g.user.company
		register_account(user)
		db.session.add(user)
		db.session.add(role)
		db.session.add(company)
		db.session.commit()
	else:
		flash(form.errors)
	return render_template('org/user/create.html', active="Company", title="Create User", form=form)

@org.route('/<user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
	permission = EditUserPermission(user_id)
	if permission.can():
		user = User.query.filter_by(id=user_id).first_or_404()
		return render_template('org/user/edit.html', active="Company", title="Edit User", user=user)
	abort(403)


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
