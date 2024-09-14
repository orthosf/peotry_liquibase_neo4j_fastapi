# src/liquibase_migration_tool/commands/loader.py
import os
import xml.etree.ElementTree as ET
from state import StateApps

class Loader:
    def __init__(self, migrations_dir):
        self.migrations_dir = migrations_dir

    def load_historical_state(self):
        print("Entered load_historical_state")
        historical_models = {}
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.xml'):
                self._apply_migration(os.path.join(self.migrations_dir, filename), historical_models)
        print("Historical Models Loaded:", historical_models)  # Debug statement
        return StateApps(historical_models)

    def _apply_migration(self, file_path, historical_models):
        print(f"Entered _apply_migration for file: {file_path}")
        with open(file_path, 'r') as file:
            content = file.read().lstrip()  # Strip leading whitespace
        print(f"File content:\n{content}")  # Debug statement
        tree = ET.ElementTree(ET.fromstring(content))
        print(f"tree: {tree}")
        root = tree.getroot()
        print(f"root: {root}")
        # Define the namespace
        #namespaces = {'neo4j': 'http://www.liquibase.org/xml/ns/neo4j'}
        #print(f"root.findall: {root.findall('.//changeSet')}")
        #for changeset in root.findall('.//changeSet'):
        namespaces = {'dbchangelog': 'http://www.liquibase.org/xml/ns/dbchangelog'}
        print(f"root.findall: {root.findall('.//dbchangelog:changeSet', namespaces)}")
        for changeset in root.findall('.//dbchangelog:changeSet', namespaces):
            print(f"Processing changeset: {ET.tostring(changeset, encoding='unicode')}")  # Debug statement
            for change in changeset:
                print(f"Processing change: {ET.tostring(change, encoding='unicode')}")  # Debug statement
                print(f"Processing change.tag: {change.tag}")
                #pdb.set_trace()  # Set a breakpoint here
                #if change.tag == '{http://www.liquibase.org/xml/ns/neo4j}cypher':
                if change.tag == '{http://www.liquibase.org/xml/ns/dbchangelog}cypher':
                    cypher_query = change.text.strip()
                    print(f"Processing cypher query: {cypher_query}")  # Debug statement
                    if cypher_query.startswith('CREATE (:'):
                        label = cypher_query.split('(:')[1].split(')')[0]
                        normalized_label = label.replace('app.app.', 'app.')
                        historical_models[f'app.{normalized_label}'] = type(normalized_label, (), {
                            '_meta': {
                                'label': f'app.{normalized_label}',
                                'properties': []
                            }
                        })
                        print(f"Added label to historical models: {label}")  # Debug statement
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
                                print(f"Added property to historical model {label}: {property_name}")  # Debug statement
                        elif 'REMOVE n.' in cypher_query:
                            property_name = cypher_query.split('REMOVE n.')[1].split('\n')[0]
                            if f'app.{normalized_label}' in historical_models:
                                historical_models[f'app.{normalized_label}']._meta['properties'] = [
                                    p for p in historical_models[f'app.{normalized_label}']._meta['properties']
                                    if p['name'] != property_name
                                ]
                                print(f"Removed property from historical model {label}: {property_name}")  # Debug statement
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
                    print(f"Added table to historical models: {table_name}")  # Debug statement
                elif change.tag == 'addColumn':
                    table_name = change.get('tableName')
                    column = change.find('.//column')
                    if f'app.{table_name.capitalize()}' in historical_models:
                        historical_models[f'app.{table_name.capitalize()}']._meta['fields'].append({
                            'name': column.get('name'),
                            'db_type': column.get('type')
                        })
                        print(f"Added column to historical model {table_name}: {column.get('name')}")  # Debug statement
                # Add more cases for other change types as needed