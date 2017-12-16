from flask_jwt_extended import jwt_required
from flask_restful import reqparse, Resource



class UserResource(Resource):
    method_decorators = [jwt_required]

    def get(self, id=None):
        return {}
        users = UserModel.query.get()

        # if id is None:
        #     return UserModel.query.get()
        # return Mongo.db().users.find_one({'_id': ObjectId(id)})

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('name', required=True)
        post_parser.add_argument('email', required=True)
        post_parser.add_argument('password', required=True)
        post_parser.add_argument('passwordRepeat', required=True)

        params = post_parser.parse_args()

        #existing_user = UserModel.query.filter(UserModel.email == params['email']).first()

        # user = Mongo.db().users.find_one({'email': params['email']})

        # if user:
        #     abort(400, message="User with this email already exist")
        #
        # if params['password'] != params['passwordRepeat']:
        #     abort(400, message="Passwords don't equals")
        #
        # user = {
        #     "name": params['name'],
        #     "email": params['email'],
        #     "password1": md5(params['password'])
        # }
        #
        # return {'_id': Mongo.db().users.insert_one(user).inserted_id}


