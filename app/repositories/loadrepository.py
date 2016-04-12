from app import app
from app import db
from app.models.load import Load
from app.repositories.lanerepository import LaneDI
from app.repositories.locationrepository import LocationDI
from app.repositories.bolrepository import BOLDI

class LoadDI():

	@staticmethod
	def createLoadFromForm(form, user):
		broker = None
		shipper = None
		load = Load(broker=broker,
					shipper=shipper,
					name=form.name.data, 
					broker_invoice=0, 
					description="",
					over_dimensional=form.over_dimensional.data,
					trailer_type=form.trailer_type.data,
					load_type=form.load_type.data,
					total_miles=form.total_miles.data,
					max_weight=form.max_weight.data,
					max_length=form.max_length.data,
					max_length_type=form.max_length_type.data,
					max_width=form.max_width.data,
					max_width_type=form.max_width_type.data,
					max_height=form.max_height.data,
					max_height_type=form.max_height_type.data)

		load.created_by = user

		load.assigned_driver = None

		stop_off_locations = []
		locations = filter(lambda location: not location.retired == "0", form.locations)
		for location in locations:
			stop_off = LocationDI.createLocationFromForm(location)
			bols = []
			for cur_BOL in filter(lambda b: not b.retired == "0", location.BOLs):
				bol = None
				if stop_off.stop_type == "Drop Off":
					bol = LocationDI.findMatchingBOLByNumber(filter((lambda loc: loc.stop_type == "Pickup"), stop_off_locations), cur_BOL)
				else:				
					bol = BOLDI.createBOLFromForm(cur_BOL)
				stop_off.BOLs.append(bol)
			db.session.add(stop_off)
			stop_off_locations.append(stop_off)
			

		load.lane = LaneDI.createLaneFromLocationArray(stop_off_locations)
		return load