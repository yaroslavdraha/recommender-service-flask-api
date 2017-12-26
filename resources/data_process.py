import ast
import json
import os

import pandas as pd
from flask import request, url_for
from flask_restful import reqparse, abort, Resource
from werkzeug.utils import secure_filename

from api.recommender.assoc_rules.assoc_rules_process import AssociationRulesProcess
from api.recommender.assoc_rules.assoc_rules_resource import AssociationRulesResource


class DataProcess(Resource):
    def post(self, action=None):
        if action == 'columns':
            file_object = request.files.get('upload_file')
            df = None

            if file_object.filename.endswith('.csv'):
                df = pd.read_csv(file_object)
            if file_object.filename.endswith('.xlsx'):
                df = pd.read_excel(file_object)

            if df.empty:
                abort(415, message="File extension is incorrect")

            return {
                'columns': list(df)
            }

        if action == 'import':
            post_parser = reqparse.RequestParser()
            post_parser.add_argument('fields', required=True)
            post_parser.add_argument('project_ref', required=True)

            params = post_parser.parse_args()

            file_object = request.files.get('upload_file')

            # Run Data processing
            a_recource = AssociationRulesResource(
                project_id=params['project_ref'],
                file_object=file_object,
                map_fields=json.loads(params['fields'])
            )

            a_rules = AssociationRulesProcess(a_recource)
            a_rules.run()

            return []

        return abort(404, message="Endpoint was not found")

    def get(self, project_id, action):
        a_recource = AssociationRulesResource(project_id=project_id)

        if action == 'collected_data':
            return a_recource.get_collected_data()
        elif action == 'itemsets':
            return a_recource.get_item_sets()

        return []
