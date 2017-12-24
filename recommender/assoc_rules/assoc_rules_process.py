# Based on user_data/<project_id> class should generate data-sets
from mlxtend.frequent_patterns import apriori, association_rules

from api.recommender.assoc_rules.assoc_rules_resource import AssociationRulesResource

import pandas as pd


class AssociationRulesProcess:
    def __init__(self, resource: AssociationRulesResource):
        self.resource = resource

    def run(self):

        df = None

        map_fields = self.resource.get_mapping()
        if map_fields:
            self._prepare_import_file(map_fields)

    def _prepare_import_file(self, fields):
        """Based on fle type need to load import data file"""
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
        rules = association_rules(frequent_itemsets, metric="lift", min_threshold=1)

        rules.to_csv(self.resource._user_data_path + "/rules.csv", encoding='utf-8', index=False,
                     columns=['antecedants', 'consequents', 'support', 'confidence', 'lift'])

