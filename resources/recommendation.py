import json

from flask import request
from flask_restful import reqparse, abort, Resource

from api.recommender.assoc_rules.assoc_rules_process import AssociationRulesProcess
from api.recommender.assoc_rules.assoc_rules_resource import AssociationRulesResource


class Recommendation(Resource):
    def post(self):
        post_parser = reqparse.RequestParser()
        post_parser.add_argument('transaction_id', required=True)
        post_parser.add_argument('items', required=True)
        params = post_parser.parse_args()

        # TODO: Get project_id from header or from Token
        project_id = "5a410660da57752e10f27178"

        transaction = {
            'transaction_id': params['transaction_id'],
            'items': json.loads(params['items'])
        }

        resource = AssociationRulesResource(project_id)
        resource.add_collected_data(transaction)

    def get(self):
        args = request.args

        if 'items' not in args:
            abort(400, message="Items parameter was missed")

        items = args['items'].split()

        if not len(items):
            abort(400, message="Items list is empty")

        # TODO: Get project_id from header or from Token
        project_id = "5a410660da57752e10f27178"

        resource = AssociationRulesResource(project_id)
        assoc_rules = AssociationRulesProcess(resource)
        assoc_rules.get_recommendation(items)
