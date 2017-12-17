from flask import request, url_for
from flask_restful import reqparse, abort, Resource
from flask import current_app as app

import pandas as pd
import json
import ast
import os

from werkzeug.utils import secure_filename

from api.recommender.data_process import AssociationRulesProcess


class DataProcess(Resource):
    def post(self, action=None):
        if action == 'columns':

            # TODO: Provide CSV loader

            df = pd.read_excel(request.files.get('upload_file'))
            return {
                'columns': list(df)
            }

        if action == 'import':
            post_parser = reqparse.RequestParser()
            post_parser.add_argument('fields', required=True)
            post_parser.add_argument('project_ref', required=True)
            params = post_parser.parse_args()

            # Write mapping.json
            user_data_path = "user_data/" + params['project_ref'] + "/data_import"
            os.makedirs(user_data_path, exist_ok=True)
            with open(user_data_path + '/mapping.json', 'w') as outfile:
                json.dump(ast.literal_eval(params['fields']), outfile)

            # Write Import file
            file = request.files['file']
            filename = secure_filename(file.filename)
            file.save(user_data_path + '/' + filename)

            info = url_for('uploaded_file', filename=filename)

            # Run Data processing
            a_rules = AssociationRulesProcess(project_id=params['project_ref'])
            a_rules.run()

        return abort(404, message="Endpoint was not found")
