from bson import ObjectId
from flask_jwt_extended import create_access_token
from flask_restful import reqparse, abort, Resource
from api.core.mongo import Mongo


class Project(Resource):

    def post(self, action=None, project_id = None):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('name', required=True)

        if not action:
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

        if action == 'tokens':
            post_parser.add_argument('project_ref', required=True)
            params = post_parser.parse_args()

            token = create_access_token({'project_id': params['project_ref']})

            token_params = {
                'token': token,
                'project_ref': params['project_ref'],
                'name': params['name']
            }

            return {
                '_id': Mongo.db().tokens.insert_one(token_params).inserted_id,
                'token': token
            }

    def get(self, action, project_id):

        if project_id is None:
            abort(404, message="User id was not selected")

        if action == 'byuser':
            return Mongo.db().projects.find({'user_ref': project_id})

        if action == 'tokens':
            return Mongo.db().tokens.find({
                'project_ref': project_id
            })

    def delete(self, action, project_id):
        if action == 'tokens':
            result = Mongo.db().tokens.delete_one({
                '_id': ObjectId(project_id)
            })

            if result.deleted_count > 0:
                return {
                    'count': result.deleted_count
                }

        abort(404, message="Action not found or affected items 0")
