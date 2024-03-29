from flask.ext.principal import Principal, Identity, AnonymousIdentity, identity_changed, RoleNeed, UserNeed, Permission
from collections import namedtuple
from functools import partial

LoadNeed = namedtuple('load', ['method', 'value'])
EditLoadNeed = partial(LoadNeed, 'edit')
DeleteLoadNeed = partial(LoadNeed, 'delete')
ViewLoadNeed = partial(LoadNeed, 'view')
AssignLoadNeed = partial(LoadNeed, 'assign')
InvoiceLoadNeed = partial(LoadNeed, 'invoice')
CompleteLoadNeed = partial(LoadNeed, 'complete')

class EditLoadPermission(Permission):
	def __init__(self, load_id):
		need = EditLoadNeed(unicode(load_id))
		super(EditLoadPermission, self).__init__(need)

class DeleteLoadPermission(Permission):
	def __init__(self, load_id):
		need = DeleteLoadNeed(unicode(load_id))
		super(DeleteLoadPermission, self).__init__(need)

class ViewLoadPermission(Permission):
	def __init__(self, load_id):
		need = ViewLoadNeed(unicode(load_id))
		super(ViewLoadPermission, self).__init__(need)

class AssignLoadPermission(Permission):
	def __init__(self, load_id):
		need = AssignLoadNeed(unicode(load_id))
		super(AssignLoadPermission, self).__init__(need)

class InvoiceLoadPermission(Permission):
	def __init__(self, load_id):
		need = InvoiceLoadNeed(unicode(load_id))
		super(InvoiceLoadPermission, self).__init__(need)

class CompleteLoadPermission(Permission):
	def __init__(self, load_id):
		need = CompleteLoadNeed(unicode(load_id))
		super(CompleteLoadPermission, self).__init__(need)

TruckNeed = namedtuple('truck', ['method', 'value'])
EditTruckNeed = partial(TruckNeed, 'edit')
DeleteTruckNeed = partial(TruckNeed, 'delete')
ViewTruckNeed = partial(TruckNeed, 'view')
RouteTruckNeed = partial(TruckNeed, 'route')

class EditTruckPermission(Permission):
	def __init__(self, truck_id):
		need = EditTruckNeed(unicode(truck_id))
		super(EditTruckPermission, self).__init__(need)

class DeleteTruckPermission(Permission):
	def __init__(self, truck_id):
		need = DeleteTruckNeed(unicode(truck_id))
		super(DeleteTruckPermission, self).__init__(need)

class ViewTruckPermission(Permission):
	def __init__(self, truck_id):
		need = ViewTruckNeed(unicode(truck_id))
		super(ViewTruckPermission, self).__init__(need)

class RouteTruckPermission(Permission):
	def __init__(self, truck_id):
		need = RouteTruckNeed(unicode(truck_id))
		super(RouteTruckPermission, self).__init__(need)

DriverNeed = namedtuple('driver', ['method', 'value'])
EditDriverNeed = partial(DriverNeed, 'edit')
DeleteDriverNeed = partial(DriverNeed, 'delete')
ViewDriverNeed = partial(DriverNeed, 'view')

class EditDriverPermission(Permission):
	def __init__(self, truck_id):
		need = EditDriverNeed(unicode(truck_id))
		super(EditDriverPermission, self).__init__(need)

class DeleteDriverPermission(Permission):
	def __init__(self, truck_id):
		need = DeleteDriverNeed(unicode(truck_id))
		super(DeleteDriverPermission, self).__init__(need)

class ViewDriverPermission(Permission):
	def __init__(self, truck_id):
		need = ViewDriverNeed(unicode(truck_id))
		super(ViewDriverPermission, self).__init__(need)

CompanyNeed = namedtuple('company', ['method', 'value'])
EditCompanyNeed = partial(CompanyNeed, 'edit')
ViewCompanyNeed = partial(CompanyNeed, 'view')

class EditCompanyPermission(Permission):
	def __init__(self, company_id):
		need = EditCompanyNeed(unicode(company_id))
		super(EditCompanyPermission, self).__init__(need)

class ViewCompanyPermission(Permission):
	def __init__(self, company_id):
		need = ViewCompanyNeed(unicode(company_id))
		super(ViewCompanyPermission, self).__init__(need)
