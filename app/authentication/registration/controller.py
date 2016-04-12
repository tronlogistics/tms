from flask import Blueprint, render_template, url_for, redirect, request, flash, session, g, current_app, jsonify, abort
from app.repositories.user import UserDI
from app.models.user import User
from app.models.company import Company
from app.repositories.companyrepository import CompanyDI
from app.emails import register_account
from app import db
from app import app
from ..authentication.controller import loginUser


def registerUserFromForm(form):
	if emailIsAlreadyRegistered(form.email.data):
		flash("This e-mail is already registerd. Please sign in!")
	user = UserDI.createUserFromForm(form)
	
	#registerUser(user)	
	company = CompanyDI.findCompanyByMCO(form.mco.data)
	if company is None:	
		company = CompanyDI.createCompanyFromForm(form)
		user.makeCompanyAdmin()
	company.users.append(user)
	print("**********")
	print user.roles
	print(company.users)
	print("**********")
	db.session.add(user)
	db.session.add(company)
	db.session.commit()
	register_account(user)
	flash("A registration e-mail has been sent to %s" % form.email.data)
	app.logger.info("User \"%s\" with role \"%s\" created" % (user.email, user.roles[0].name))

def registerUserFromJSON(json):
	if emailIsAlreadyRegistered(json.get('email')):
		flash("This e-mail is already registerd. Please sign in!")
	user = UserDI.createUserFromJSON(json)	
	company = CompanyDI.findCompanyByMCO(json.get('mco'))
	role = Role.findRoleByType(json.get('type'))
	if company is None:	
		company = CompanyDI.createCompanyFromJSON(json)
		user.makeCompanyAdmin()
	user.roles.append(role)
	company.users.append(user)
	
	if role.code == "owner_operator":
		truck = Truck.createTruckFromJSON(json)
		driver = Driver.createDriverFromUserData(user)
		driver.driver_type = "Owner Operator"
		truck.driver = driver
		company.fleet.trucks.append(truck)
		company.fleet.drivers.append(driver)
		db.session.add(truck)
		db.session.add(driver)

	
	loginUser(user)

	db.session.add(user)
	db.session.add(company)
	db.session.commit()

def emailIsAlreadyRegistered(email):
	return User.query.filter_by(email=email).first() is not None

def activateUser(user):
	user.activate()
	db.session.add(user)
	db.session.commit()

def handlePasswordReset(user, form):
	user.set_password(form.password.data)
	db.session.add(user)
	db.session.commit()
	flash("Your password has been updated.")

def setPasswordForUser(user, form):
	user.set_password(form.password.data)
	loginUser(user)
