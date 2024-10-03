import os
import xml.etree.ElementTree as ET
from state import StateApps

class StatuslogLoader:
    def __init__(self, migrations_dir):
        self.migrations_dir = migrations_dir

    def load_historical_statuslog(self):
        historical_statuslog_models = {}
        for filename in sorted(os.listdir(self.migrations_dir), reverse=True):
            if filename.endswith('.xml') and filename.startswith('statuslog'):
                self._apply_statuslog(os.path.join(self.migrations_dir, filename), historical_statuslog_models)
        return StateApps(historical_statuslog_models)

    def _apply_statuslog(self, file_path, historical_statuslog_models):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                print(f"Content of {file_path}:")
                print(content)
                print("=" * 50)
            tree = ET.parse(file_path)
            root = tree.getroot()

            for model in root.findall('.//model'):
                model_name = model.get('name')
                model_type = model.get('type')
                is_new_element = model.find('is_new')
                is_new = is_new_element.text.lower() == 'true' if is_new_element is not None else False

                if is_new or model_name not in historical_statuslog_models:
                    fields = []
                    for field in model.findall('.//field'):
                        fields.append({
                            'name': field.get('name'),
                            'property': field.get('property'),
                            'index': field.get('index'),
                            'constraints': field.get('constraints')
                        })

                    relationships = []
                    for relationship in model.findall('.//relationship'):
                        relationships.append({
                            'name': relationship.get('name'),
                            'property': relationship.get('property'),
                            'model': relationship.get('model'),
                            'relation_name': relationship.get('relation_name'),
                            'direction': relationship.get('direction')
                        })

                    historical_statuslog_models[model_name] = type(model_name, (), {
                        '_meta': {
                            'label': model_name,
                            'type': model_type,
                            'fields': fields,
                            'relationships': relationships
                        }
                    })
        except ET.ParseError as e:
            print(f"Error parsing XML file: {file_path}")
            print(f"Error details: {e}")
            print("Skipping this file and continuing with others.")
        except Exception as e:
            print(f"Unexpected error while processing file: {file_path}")
            print(f"Error details: {e}")
            print("Skipping this file and continuing with others.")