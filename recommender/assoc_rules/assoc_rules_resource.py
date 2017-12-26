import json
import os
import pandas as pd

from werkzeug.utils import secure_filename
from flask_restful import abort


class AssociationRulesResource:

    def __init__(self, project_id, **kwargs):
        """
        :param project_id
        :param file_object
        :param map_fields
        """

        self._map_fields = kwargs.get('map_fields')
        self._file_object = kwargs.get('file_object')
        self._project_id = project_id
        self._user_data_path = "user_data/" + self._project_id
        self._user_data_import_path = "user_data/" + self._project_id + "/data_import"

    def upload_file_object(self):
        """
        Upload imported file to server
        Should be called after AR processing
        """
        filename = secure_filename(self._file_object.filename)
        self._file_object.save(self._user_data_import_path + '/' + filename)

    def get_mapping(self):
        """
        Return fields mapping from file or save and return
        :rtype: dict
        """
        # if self._map_fields and type(self._map_fields) is dict:
        #     return self._map_fields

        mappings = self._map_fields
        file_exist = self._is_file_exist('data_import/mapping.json')

        if mappings is None and file_exist:
            mappings = self._read_mapping()
        elif mappings:
            self._write_map_fields()

        parsed = {}
        for name, field_type in mappings.items():
            if field_type not in parsed:
                parsed[field_type] = []

            parsed[field_type].append(name)

        # validation - at least one transaction_id and name
        if not parsed.get('name'):
            abort(415, message="You have to mark at least one field as Item name/description")

        if not parsed.get('transaction_id'):
            abort(415, message="You have to mark at least one field as Unique action ID")

        self._map_fields = parsed
        return parsed

    def get_import_file(self):
        """
        Return file object received from import or
        return file path with type for load via pandas
        or return None if import file was not found
        """
        if self._file_object:
            return self._file_object

        csv = 'data_import/imported_file.csv'
        excel = 'data_import/imported_file.xlsx'

        if self._is_file_exist(csv):
            return {
                'path': self._user_data_path + "/" + csv,
                'type': 'csv'
            }

        if self._is_file_exist(excel):
            return {
                'path': self._user_data_path + "/" + excel,
                'type': 'excel'
            }

    def get_collected_file_path(self):
        """
        Get collected transaction data from data_collected.csv
        """
        path = self._user_data_path + '/collected.csv'

        if self._is_file_exist('collected.csv'):
            return path

        return None

    def get_collected_data(self):
        """
        Get collected via API data from csv file
        """
        if not self.get_collected_file_path():
            return {}

        data = pd.read_csv(self._user_data_path + "/collected.csv", sep=';')
        return data.to_dict('records')

    def get_item_sets(self):
        """
        Get generated rules for current project
        """
        if not self._is_file_exist('rules.csv'):
            return []

        rules = pd.read_csv(self._user_data_path + "/rules.csv", sep=';')
        return rules.to_dict('records')

    def _write_map_fields(self):
        """Save json configuration for fields mapping to mapping.json appropriate file"""
        if self._map_fields is None:
            return

        os.makedirs(self._user_data_import_path, exist_ok=True)
        with open(self._user_data_import_path + '/mapping.json', 'w') as outfile:
            json.dump(self._map_fields, outfile)

    def _is_file_exist(self, filename):
        """
        Test whether a file related to project_id exists.
        Returns False for broken symbolic links
        :param filename
        :return boolean
        """
        try:
            st = os.stat(self._user_data_path + "/" + filename)
        except os.error:
            return False
        return True

    def _read_mapping(self):
        return json.load(open(self._user_data_import_path + '/mapping.json'))
