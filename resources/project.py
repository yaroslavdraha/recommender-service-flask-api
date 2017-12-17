from flask_restful import reqparse, abort, Resource
from api.core.mongo import Mongo


class Project(Resource):

    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('name', required=True)
        post_parser.add_argument('user_ref', required=True)

        params = post_parser.parse_args()

        if not params['name']:
            abort(400, message="Project name cannot be empty")

        project_params = {
            'user_ref': params['user_ref'],
            'name': params['name']
        }

        project = Mongo.db().projects.find_one(project_params)

        if project:
            abort(400, message="Your already have project with this name")

        return {'_id': Mongo.db().projects.insert_one(project_params).inserted_id}
