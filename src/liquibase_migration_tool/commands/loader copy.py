# src/liquibase_migration_tool/commands/loader.py
import os
import xml.etree.ElementTree as ET
from state import StateApps

class Loader:
    def __init__(self, migrations_dir):
        self.migrations_dir = migrations_dir

    def load_historical_state(self):
        historical_models = {}
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.xml'):
                self._apply_migration(os.path.join(self.migrations_dir, filename), historical_models)
        print("Historical Models Loaded:", historical_models)  # Debug statement
        return StateApps(historical_models)

    def _apply_migration(self, file_path, historical_models):
        with open(file_path, 'r') as file:
            content = file.read().lstrip()  # Strip leading whitespace
        tree = ET.ElementTree(ET.fromstring(content))
        root = tree.getroot()
        namespaces = {'dbchangelog': 'http://www.liquibase.org/xml/ns/dbchangelog'}
        for changeset in root.findall('.//dbchangelog:changeSet', namespaces):
            for change in changeset:
                if change.tag == '{http://www.liquibase.org/xml/ns/dbchangelog}cypher':
                    cypher_query = change.text.strip()
                    if cypher_query.startswith('CREATE (:'):
                        label = cypher_query.split('(:')[1].split(')')[0]
                        normalized_label = label.replace('app.app.', 'app.')
                        historical_models[f'app.{normalized_label}'] = type(normalized_label, (), {
                            '_meta': {
                                'label': f'app.{normalized_label}',
                                'properties': []
                            }
                        })
                    elif cypher_query.startswith('MATCH (n:'):
                        label = cypher_query.split('(n:')[1].split(')')[0]
                        normalized_label = label.replace('app.app.', 'app.')
                        if 'SET n.' in cypher_query:
                            property_name = cypher_query.split('SET n.')[1].split(' =')[0]
                            if f'app.{normalized_label}' in historical_models:
                                historical_models[f'app.{normalized_label}']._meta['properties'].append({
                                    'name': property_name,
                                    'db_type': 'string'  # Assume string type for simplicity
                                })
                        elif 'DETACH DELETE n' in cypher_query or 'DELETE n' in cypher_query:
                            if f'app.{normalized_label}' in historical_models:
                                del historical_models[f'app.{normalized_label}']
                        elif 'REMOVE n.' in cypher_query:
                            property_name = cypher_query.split('REMOVE n.')[1].split('\n')[0]
                            if f'app.{normalized_label}' in historical_models:
                                historical_models[f'app.{normalized_label}']._meta['properties'] = [
                                    p for p in historical_models[f'app.{normalized_label}']._meta['properties']
                                    if p['name'] != property_name
                                ]
                elif change.tag == 'createTable':
                    table_name = change.get('tableName')
                    fields = []
                    for column in change.findall('.//column'):
                        fields.append({
                            'name': column.get('name'),
                            'db_type': column.get('type')
                        })
                    historical_models[f'app.{table_name.capitalize()}'] = type(table_name.capitalize(), (), {
                        '_meta': {
                            'label': f'app.{table_name.capitalize()}',
                            'db_table': table_name,
                            'fields': fields
                        }
                    })
                elif change.tag == 'addColumn':
                    table_name = change.get('tableName')
                    column = change.find('.//column')
                    if f'app.{table_name.capitalize()}' in historical_models:
                        historical_models[f'app.{table_name.capitalize()}']._meta['fields'].append({
                            'name': column.get('name'),
                            'db_type': column.get('type')
                        })
        for model in root.findall('.//model'):
            label = model.get('name')
            properties = []
            for field in model.findall('.//field'):
                properties.append({
                    'name': field.get('name'),
                    'db_type': field.get('property')
                })
            historical_models[f'app.{label}'] = type(label, (), {
                '_meta': {
                    'label': f'app.{label}',
                    'properties': properties
                }
            })