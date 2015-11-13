from app import app, authAPI, lm, api
from app.models import User
from flask import Blueprint, request, session, g, current_app, jsonify, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource, reqparse, fields, marshal

@authAPI.verify_password
def verify_password(email_or_token, password):
    
    # first try to authenticate by token
    user = User.verify_auth_token(email_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(email=email_or_token).first()
        if not user or not user.check_password(password):
            return False
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







bol_fields = {
    
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
        loads = g.user.company.loads
        for load in loads:
            load.lane.locations
        return {'loads': [marshal(load, load_fields) for load in g.user.company.loads]}

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
        load = [load for load in g.user.company.loads if load.id == id]
        if len(load) == 0:
            abort(404)
        return {'load': marshal(load[0], load_fields)}

class LocationAPI(Resource):
    decorators = [authAPI.login_required]
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        #self.reqparse.add_argument('number', type=str, default="",
        #                           location='json')
        super(LocationAPI, self).__init__()

    def get(self, load_id, location_id):
        load = [load for load in g.user.company.loads if load.id == load_id]
        location = None
        for cur_location in load[0].lane.locations:
            if cur_location.id == location_id:
                location = cur_location
        if len(load) == 0:
            abort(404)
        return {'location': marshal(location, location_fields)}




#class TaskAPI(Resource):
#    decorators = [auth.login_required]

#    def __init__(self):
#        self.reqparse = reqparse.RequestParser()
#        self.reqparse.add_argument('title', type=str, location='json')
#        self.reqparse.add_argument('description', type=str, location='json')
#        self.reqparse.add_argument('done', type=bool, location='json')
#        super(TaskAPI, self).__init__()

#    def get(self, id):
#        task = [task for task in tasks if task['id'] == id]
#        if len(task) == 0:
#            abort(404)
#        return {'task': marshal(task[0], task_fields)}

#    def put(self, id):
#        task = [task for task in tasks if task['id'] == id]
#        if len(task) == 0:
#            abort(404)
#        task = task[0]
#        args = self.reqparse.parse_args()
#        for k, v in args.items():
#            if v is not None:
#                task[k] = v
#        return {'task': marshal(task, task_fields)}

#    def delete(self, id):
#        task = [task for task in tasks if task['id'] == id]
#        if len(task) == 0:
#            abort(404)
#        tasks.remove(task[0])
#        return {'result': True}


api.add_resource(LoadListAPI, '/todo/api/v1.0/loads', endpoint='loads')
api.add_resource(LoadAPI, '/todo/api/v1.0/loads/<int:id>', endpoint='load')
api.add_resource(LocationAPI, '/todo/api/v1.0/loads/<int:load_id>/locations/<int:location_id>', endpoint='location')
#api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')
