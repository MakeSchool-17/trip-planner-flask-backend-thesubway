from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
from flask.ext.bcrypt import bcrypt
from functools import wraps

# Basic Setup
app = Flask(__name__)
mongo = MongoClient('localhost', 27017)
app.db = mongo.develop_database
api = Api(app)
app.bcrypt_rounds = 12


def hash_password(password, salt):
    encoded = password.encode('utf-8')
    return bcrypt.hashpw(encoded, salt)


def check_auth(username, password):
    # retrieve api pw key from database.
    user = app.db.users.find_one({"name": username})
    if user is None:
        return False
    password_hash = user['password']
    password_encrypted = hash_password(password, salt=password_hash)
    return password_encrypted == password_hash


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = {"error": "Basic Auth Required."}
            resp = jsonify(message)
            resp.status_code = 401
            return resp
        return f(*args, **kwargs)
    return decorated


# Implement REST Resource
# [Ben-G] Example breakpoints can be removed once you've implemeted the trip API
class MyObject(Resource):

    def post(self):
        new_myobject = request.json
        myobject_collection = app.db.myobjects
        result = myobject_collection.insert_one(request.json)

        myobject = myobject_collection.find_one({"_id": ObjectId(result.inserted_id)})

        return myobject

    def get(self, myobject_id):
        myobject_collection = app.db.myobjects
        myobject = myobject_collection.find_one({"_id": ObjectId(myobject_id)})

        if myobject is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return myobject


class Trip(Resource):

    @requires_auth
    def post(self):
        trip_collection = app.db.trips
        request.json['owner'] = request.authorization['username']
        result = trip_collection.insert_one(request.json)
        trip = trip_collection.find_one({"_id": ObjectId(result.inserted_id)})
        return trip

    @requires_auth
    def get(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})

        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            return trip

    def put(self, trip_id):
        # this calls get first, to find a property.
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        myobject_collection = app.db.myobjects
        result = myobject_collection.update_one(request.json)
        return result

    @requires_auth
    def delete(self, trip_id):
        trip_collection = app.db.trips
        trip = trip_collection.find_one({"_id": ObjectId(trip_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        else:
            trip_collection.delete_one({"_id": ObjectId(trip_id)})
            return trip_collection.find_one({"_id": ObjectId(trip_id)})


class User(Resource):

    # def get_all(self, trip_ids):
    #     trips = []
    #     responses = []
    #     for each_id in trip_ids:
    #         each_trip = trip_collection.find_one({"_id": ObjectId(each_id)})
    #         trips.append(each_trip)
    #         if each_trip is None:
    #             response = jsonify(data=[])
    #             response.status_code = 404
    #             responses.append(response)
    #     return trips
    # def __init__(self):
    #     self.trips = []
    #     self.name = None
    #     self.password_hash = None

    def post(self):
        user_collection = app.db.users
        password = request.json["password"]
        pass_hash = hash_password(password, bcrypt.gensalt(app.bcrypt_rounds))
        request.json["password"] = pass_hash
        request.json["trips"] = []

        result = user_collection.insert_one(request.json)
        user = user_collection.find_one({"_id": ObjectId(result.inserted_id)})
        del user['password']  # DO NOT return password back to the client!!!
        return user

    @requires_auth
    def get(self, user_id):
        user_collection = app.db.users
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if user is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        del user['password']  # DO NOT return password back to the client!!!
        return user

    def put(self, user_id):
        user_collection = app.db.users
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if trip is None:
            response = jsonify(data=[])
            response.status_code = 404
            return response
        result = user_collection.update_one(request.json)
        return result

# Add REST resource to API
api.add_resource(MyObject, '/myobject/', '/myobject/<string:myobject_id>')
api.add_resource(Trip, '/trip/', '/trip/<string:trip_id>')
api.add_resource(User, '/user/', '/user/<string:user_id>')
# provide a custom JSON serializer for flaks_restful


@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    # app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    # app.run(debug=True)
    check_auth("test", "testpw")
