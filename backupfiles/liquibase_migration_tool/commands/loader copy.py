import os
import xml.etree.ElementTree as ET
from .state import StateApps

class Loader:
    def __init__(self, migrations_dir):
        self.migrations_dir = migrations_dir

    def load_historical_state(self):
        historical_models = {}
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.xml'):
                self._apply_migration(os.path.join(self.migrations_dir, filename), historical_models)
        return StateApps(historical_models)

    def _apply_migration(self, file_path, historical_models):
        tree = ET.parse(file_path)
        root = tree.getroot()

        for changeset in root.findall('.//changeSet'):
            for change in changeset.findall('.//cypher'):
                cypher_query = change.text.strip()
                if cypher_query.startswith('CREATE (:'):
                    label = cypher_query.split('(:')[1].split(')')[0]
                    historical_models[f'app.{label}'] = type(label, (), {
                        '_meta': {
                            'label': f'app.{label}',
                            'properties': []
                        }
                    })
                elif cypher_query.startswith('MATCH (n:'):
                    label = cypher_query.split('(n:')[1].split(')')[0]
                    if 'SET n.' in cypher_query:
                        property_name = cypher_query.split('SET n.')[1].split(' =')[0]
                        if f'app.{label}' in historical_models:
                            historical_models[f'app.{label}']._meta['properties'].append({
                                'name': property_name,
                                'db_type': 'string'  # Assume string type for simplicity
                            })
                    elif 'REMOVE n.' in cypher_query:
                        property_name = cypher_query.split('REMOVE n.')[1].split('\n')[0]
                        if f'app.{label}' in historical_models:
                            historical_models[f'app.{label}']._meta['properties'] = [
                                p for p in historical_models[f'app.{label}']._meta['properties']
                                if p['name'] != property_name
                            ]
                # Add more cases for other change types as needed