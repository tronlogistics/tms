from app import app
from app import db
from app.models.bol import BOL

class BOLDI():

	@staticmethod
	def createBOLFromForm(form):
		bol = BOL(number=form.bol_number.data,
					number_units=form.number_units.data,
					weight=form.weight.data,
					commodity_type=form.commodity_type.data,
					dim_length=form.dim_length.data,
					dim_length_type=form.dim_length_type.data,
					dim_width=form.dim_width.data,
					dim_width_type=form.dim_width_type.data,
					dim_height=form.dim_height.data,
					dim_height_type=form.dim_height_type.data)
		return bol