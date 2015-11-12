from app import app, authAPI, lm, api
from app.models import User
from flask import Blueprint, request, session, g, current_app, jsonify, abort
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restful import Api, Resource, reqparse, fields, marshal


loads = [{
        'id': 1,
        'number': 12,
        'type': "TL",
        'trailer': "Flatbed",
        'totalMiles': 500,
        'maxWeight': 50000,
        'overDimensional': False,
        'maxLength': "40",
        'maxLengthType': "inches",
        'maxWidth': "32",
        'maxWidthType': "inches",
        'maxHeight': "45",
        'maxHeightType': "inches"
        
          },
          {
        'id': 2,
        'number': 13,
        'type': "TL",
        'trailer': "Flatbed",
        'totalMiles': 500,
        'maxWeight': 50000,
        'overDimensional': False,
        'maxLength': "40",
        'maxLengthType': "inches",
        'maxWidth': "32",
        'maxWidthType': "inches",
        'maxHeight': "45",
        'maxHeightType': "inches"
        
          }]

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




load_fields = {
    'id': fields.String,
    'number': fields.String,
    'type': fields.String,
    'trailer': fields.String
}


class LoadListAPI(Resource):
    decorators = [authAPI.login_required]#[authAPI.verify_password, authAPI.login_required]

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('number', type=str, default="",
                                   location='json')
        super(LoadListAPI, self).__init__()

    def get(self):
        print("testing 123")
        return {'loads': [marshal(load, load_fields) for load in g.user.company.loads]}

class LoadAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('number', type=str, default="",
                                   location='json')
        super(LoadAPI, self).__init__()

    def get(self, id):
        load = [load for load in loads if load['id'] == id]
        if len(load) == 0:
            abort(404)
        return {'load': marshal(load[0], load_fields)}




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
#api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint='task')
