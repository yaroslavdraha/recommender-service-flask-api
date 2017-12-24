import ast
import json
import os

from werkzeug.utils import secure_filename


class AssociationRulesResource:

    def __init__(self, project_id, **kwargs):
        """
        :param project_id
        :param file_object
        :param map_fields
        """

        self._map_fields = kwargs['map_fields']
        self._file_object = kwargs['file_object']
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
        path = self._user_data_path + '/data_collected.csv'

        if self._is_file_exist(path):
            return path

        return None

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
