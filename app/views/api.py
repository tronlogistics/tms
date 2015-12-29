from app import app, authAPI, lm, api, db
from app.models import User, Load, Location, LocationStatus, LongLat, Truck
from flask import Blueprint, request, session, g, current_app, jsonify, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from datetime import datetime
import json

@authAPI.verify_password
def verify_password(email_or_token, password):
    
    # first try to authenticate by token
    print"%s - %s" % (email_or_token, password)
    print email_or_token
    user = User.verify_auth_token(email_or_token)
    print user
    print "%s" % (not user)
    if not user:
        # try to authenticate with username/password
        print "finding user %s" % email_or_token
        print "finding user %s" % password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.check_password(password):
            return False
        print "user found"
    g.user = user
    return True



#    tracker = db.relationship("LongLat", lazy='dynamic')
    

    #children
#    lane = db.relationship('Lane', uselist=False, backref='load')

    #assignments
#    truck_id = db.Column(db.Integer, db.ForeignKey('Truck.id'))
#    truck = db.relationship('Truck', backref='loads')

#    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
#    created_by = db.relationship("User")

#    bids = db.relationship("Bid", backref="load")

bol_fields = {
    'id': fields.String,
    'number': fields.String,
    'number_units': fields.String,
    'weight': fields.String,
    'commodity_type': fields.String,
    'dim_length': fields.String,
    'dim_length_type': fields.String,
    'dim_width': fields.String,
    'dim_width_type': fields.String,
    'dim_height': fields.String,
    'dim_height_type': fields.String
}
contact_fields = {
    'name': fields.String,
    'email': fields.String,
    'phone': fields.String
}

address_fields = {
    'address1': fields.String,
    'address2': fields.String,
    'city': fields.String,
    'state': fields.String,
    'postal_code': fields.String,
    'latitude': fields.String,
    'longitude': fields.String
}

location_status_fields = {
    'id': fields.String,
    'status': fields.String,
    'created_on': fields.DateTime(dt_format='rfc822')
}

location_fields = {
    'id': fields.String,
    'address': fields.Nested(address_fields),
    'arrival_date': fields.String,
    'notes': fields.String,
    'contact': fields.Nested(contact_fields),
    'stop_number': fields.String,
    'type': fields.String,
    'latitude': fields.String,
    'longitude': fields.String,
    'status_history': fields.List(fields.Nested(location_status_fields)),
    'BOLs': fields.List(fields.Nested(bol_fields))
}

lane_fields = {
    'locations': fields.List(fields.Nested(location_fields))
}

load_fields = {
    'id': fields.String,
    'name': fields.String,
    'status': fields.String,
    'trailer_group': fields.String,
    'trailer_type': fields.String,
    'load_type': fields.String,
    'total_miles': fields.String,
    'over_dimensional': fields.Boolean,
    'carrier_invoice': fields.String,
    'broker_invoice': fields.String,
    'description': fields.String,
    'comments': fields.String,
    'max_weight': fields.String,
    'max_length': fields.String,
    'max_length_type': fields.String,
    'max_width': fields.String,
    'max_width_type': fields.String,
    'max_height': fields.String,
    'max_height_type': fields.String,
    'lane': fields.Nested(lane_fields)
}


class LoadListAPI(Resource):
    #decorators = [authAPI.login_required]#[authAPI.verify_password, authAPI.login_required]
    decorators = [authAPI.login_required]
    def __init__(self):
        #self.reqparse = reqparse.RequestParser()
        #self.reqparse.add_argument('id', type=str, required=True,
        #                           help='No task title provided',
        #                           location='json')
        #self.reqparse.add_argument('number', type=str, default="",
        #                           location='json')
        super(LoadListAPI, self).__init__()

    def get(self):
        print json.dumps(request.json)
		try:
			loads = []
			for driver in g.user.driver_instances:
				for load in driver.truck.loads:
					loads.append(load)
			return {'loads': [marshal(load, load_fields) for load in filter(lambda load: load.status != "Delivered", loads)]}
		except:
			print "Unexpected error:", sys.exc_info()[0]

class LoadAPI(Resource):
    decorators = [authAPI.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        #self.reqparse.add_argument('number', type=str, default="",
        #                           location='json')
        super(LoadAPI, self).__init__()

    def get(self, id):
        load = Load.query.get_or_404(int(id))
        return {'load': marshal(load, load_fields)}

class LocationAPI(Resource):
    decorators = [authAPI.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('status', type=str, required=False,
                                   help='No task title provided',
                                   location='json')
        #self.reqparse.add_argument('number', type=str, default="",
        #                           location='json')
        super(LocationAPI, self).__init__()

    def get(self, load_id, location_id):
        print("-----GET------")
        load = [load for load in g.user.company.loads if load.id == load_id]
        location = None
        for cur_location in load[0].lane.locations:
            if cur_location.id == location_id:
                location = cur_location
        if location is None:
			abort(404)
        return {'location': marshal(location, location_fields)}

    def put(self, load_id, location_id):
        load = [load for load in g.user.company.loads if load.id == load_id]
        location = None
        for cur_location in load[0].lane.locations:
            if cur_location.id == location_id:
                location = cur_location
        args = self.reqparse.parse_args()
        print args
        for k, status in args.iteritems():
            if status != None:
                status_history = LocationStatus(status=status, created_on=datetime.utcnow())
                location.status_history.append(status_history)
                location.status = status
                db.session.add(status_history)
        load[0].setStatus("")
        db.session.add(location)
        db.session.commit()
        return jsonify( { 'task': 'task' } )

class LongLatAPI(Resource):
    decorators = [authAPI.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('longitude', type=str, required=False,
                                   help='No longitude provided',
                                   location='json')
        self.reqparse.add_argument('latitude', type=str, required=False,
                                   help='No latitude provided',
                                   location='json')
        #self.reqparse.add_argument('number', type=str, default="",
        #                           location='json')
        super(LongLatAPI, self).__init__()

    def post(self):
        print json.dumps(request.json)
        for driver in g.user.driver_instances:
            print "found instance"
            if driver.truck is not None:
                geo = LongLat(latitude=request.json.get('location').get('coords').get('latitude'),
                                longitude=request.json.get('location').get('coords').get('longitude'))
                driver.truck.tracker.append(geo)
                db.session.add(geo)
                db.session.add(driver.truck)
        db.session.commit()
        return jsonify( { 'response': 'success' } )

api.add_resource(LoadListAPI, '/todo/api/v1.0/loads', endpoint='loads')
api.add_resource(LoadAPI, '/todo/api/v1.0/loads/<int:id>', endpoint='load')
api.add_resource(LocationAPI, '/todo/api/v1.0/loads/<int:load_id>/locations/<int:location_id>', endpoint='location')
api.add_resource(LongLatAPI, '/todo/api/v1.0/longlat', endpoint='longlat')
