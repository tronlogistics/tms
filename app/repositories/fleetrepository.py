from app import app
from app import db
from app.models.fleet import Fleet

class FleetDI():
	@staticmethod
	def createFleet():
		fleet = Fleet()
		return fleet 