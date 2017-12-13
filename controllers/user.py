from _md5 import md5

from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import reqparse, abort, Resource
from api.core.mongo import Mongo


class User(Resource):
    method_decorators = [jwt_required]

    def get(self, id=None):
        if id is None:
            return Mongo.db().users.find({})
        return Mongo.db().users.find_one({'_id': ObjectId(id)})

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('name', required=True)
        post_parser.add_argument('email', required=True)
        post_parser.add_argument('password', required=True)
        post_parser.add_argument('passwordRepeat', required=True)

        params = post_parser.parse_args()

        user = Mongo.db().users.find_one({'email': params['email']})

        if user:
            abort(400, message="User with this email already exist")

        if params['password'] != params['passwordRepeat']:
            abort(400, message="Passwords don't equals")

        user = {
            "name": params['name'],
            "email": params['email'],
            "password1": md5(params['password'])
        }

        return {'_id': Mongo.db().users.insert_one(user).inserted_id}


