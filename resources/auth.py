import hashlib
from flask_jwt_extended import create_access_token
from flask_restful import Resource, reqparse, abort
from werkzeug.security import safe_str_cmp
from api.core.mongo import Mongo
from api.core.response import Response


# TODO: Refactor this functionality. Need to provide 2 tokens: access and refresh
class Auth(Resource):

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('username', required=True)
        post_parser.add_argument('password', required=True)

        params = post_parser.parse_args()

        user = Mongo.db().users.find_one({'email': params['username']})

        if user is None or not safe_str_cmp(user['password'], hashlib.md5(params['password'].encode('utf-8')).hexdigest()):
            abort(400, message="Credentials are incorrect")

        user.pop('password')

        # user = {'id': str(user['_id'])}

        return {
            'token': create_access_token({'id': str(user['_id'])}),
            'model': Response.convert_mongo_item(user)
        }

        # return {
        #     'access_token': create_access_token(identity=user),
        #     'refresh_token': create_refresh_token(identity=user)
        # }
