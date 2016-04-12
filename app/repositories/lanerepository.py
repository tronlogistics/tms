from app import app
from app import db
from app.models.lane import Lane

class LaneDI():

	@staticmethod
	def createLaneFromLocationArray(locations):
		lane = Lane(locations)
		return lane