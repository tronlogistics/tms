from app import app
from app import db
from app.models.role import Role

class RoleDI():

	@staticmethod
	def findRoleByType(roleCode):
		return Role.query.filter_by(code=roleCode).first()
