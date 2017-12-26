# Based on user_data/<project_id> class should generate data-sets
from flask_restful import abort
from mlxtend.frequent_patterns import apriori, association_rules
from api.recommender.assoc_rules.assoc_rules_resource import AssociationRulesResource

import pandas as pd


# TODO:
# 1) Functionality for Meta-data fields
# 2) Give possibility to change support and lift by user
# 3) Validation for field mapping

class AssociationRulesProcess:
    def __init__(self, resource: AssociationRulesResource):
        self.resource = resource

    def run(self):
        # TODO: Implement case when imported file was not found, but we want to run process
        map_fields = self.resource.get_mapping()
        if map_fields:
            self._generate_rules(map_fields)
        else:
            abort(404, message="Mapping fields was not found, or something went wrong with fields save")

    def add_transaction(self, transaction_data):
        self.resource.add_collected_data(transaction_data)

    def get_recommendation(self, items):
        pass

    def _generate_rules(self, fields):
        """
        The main method for rules generation based on project, collected imported data
        """
        file = self.resource.get_import_file()

        df_import = pd.DataFrame()
        if type(file) is dict:
            if file.type == 'csv':
                df_import = pd.read_csv(file.path)
            if file.type == 'excel':
                df_import = pd.read_excel(file.path)

        if file.filename.endswith('.csv'):
            df_import = pd.read_csv(file)
        if file.filename.endswith('.xlsx'):
            df_import = pd.read_excel(file)

        # edit df
        # 1. remove empty symbols from item names
        field_name = fields['name'][0]
        df_import[field_name] = df_import[field_name].str.strip()

        # 2. remove rows without transaction_id
        field_transaction_id = fields['transaction_id'][0]
        df_import.dropna(axis=0, subset=[field_transaction_id], inplace=True)

        # 3. Merge with data_collected.csv
        df_collected = pd.DataFrame()

        collected_path = self.resource.get_collected_file_path()
        if collected_path:
            df_collected = pd.read_csv(collected_path)

        # 4. Build data_processed.csv
        df = pd.DataFrame()
        if not df_collected.empty and not df_import.empty:
            df = df_import.append(df_collected)
        elif not df_collected.empty:
            df = df_collected
        elif not df_import.empty:
            df = df_import

        if df.empty:
            return

        # Create table with transactions
        basket = (df.groupby([field_transaction_id, field_name])[field_transaction_id]
                  .sum().unstack().reset_index().fillna(0)
                  .set_index(field_transaction_id))

        def encode_units(x):
            if x:
                return 1
            if x == 0:
                return 0

        basket_sets = basket.applymap(encode_units)

        frequent_itemsets = apriori(basket_sets, min_support=0.2, use_colnames=True)
        rules = association_rules(frequent_itemsets)

        rules['antecedants'] = rules['antecedants'].str.join(', ')
        rules['consequents'] = rules['consequents'].str.join(', ')
        rules.to_csv(self.resource._user_data_path + "/rules.csv",
                     sep=';', index=False, encoding='utf-8',
                     columns=['antecedants', 'consequents', 'support', 'confidence', 'lift'])