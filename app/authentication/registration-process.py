from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app, jsonify, abort
from app.models import User, Role, Address, Company

class RegistrationProcess():

	def registerUserFromForm(form):
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
