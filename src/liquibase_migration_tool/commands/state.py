# src/liquibase_migration_tool/commands/state.py

import xml.etree.ElementTree as ET
from termcolor import colored

class StateApps:
    def __init__(self, models):
        self.models = models

    @classmethod
    def from_apps(cls, apps):
        models = {}
        for model in apps.get_models():
            models[model._meta['label']] = model
        print("Models from apps:", models)  # Debug statement
        return cls(models)

    @classmethod
    def from_statuslog(cls, statuslog_path):
        models = {}
        tree = ET.parse(statuslog_path)
        root = tree.getroot()
        for model in root.findall('.//model'):
            label = model.get('name')
            properties = []
            for field in model.findall('.//field'):
                properties.append({
                    'name': field.get('name'),
                    'db_type': field.get('property')
                })
            models[f'app.{label}'] = type(label, (), {
                '_meta': {
                    'label': f'app.{label}',
                    'properties': properties,
                    'relationships': []  # Ensure relationships key exists
                }
            })
        return cls(models)

    def log_contents(self):
        print("StateApps contents:")
        for label, model in self.models.items():
            print(f"Model: {label}")
            print(f"  Attributes:")
            for attr_name, attr_value in model.__dict__.items():
                if not attr_name.startswith('__'):
                    msg = f"    {attr_name}: {attr_value}"
                    print(colored(msg, "yellow"))
            print(f"  Meta:")
            for meta_key, meta_value in model._meta.items():
                msg = f"    {meta_key}: {meta_value}"
                print(colored(msg, "yellow"))
            print()