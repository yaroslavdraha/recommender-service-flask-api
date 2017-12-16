import hashlib

from flask_restful import reqparse, abort, Resource
from api.core.mongo import Mongo


class User(Resource):
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
            "password": hashlib.md5(params['password'].encode('utf-8')).hexdigest()
        }

        return {'_id': Mongo.db().users.insert_one(user).inserted_id}
