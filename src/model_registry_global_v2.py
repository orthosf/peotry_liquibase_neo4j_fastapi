import os
import importlib
import inspect
from neomodel import StructuredNode

class ModelRegistry:
    def __init__(self):
        self._models = {}

    def register_models_from_directory(self, directory):
        # Recursively search for models.py files in all subdirectories
        for root, _, files in os.walk(directory):
            if 'models.py' in files:
                module_name = root.replace('/', '.') + '.models'
                self._import_and_register_models(module_name)

    def _import_and_register_models(self, module_name):
        # Dynamically import the models.py file
        try:
            module = importlib.import_module(module_name)
        except ModuleNotFoundError as e:
            print(f"Module {module_name} not found: {e}")
            return

        # Register all classes that are subclasses of StructuredNode (i.e., Neomodel models)
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and issubclass(obj, StructuredNode) and obj is not StructuredNode:
                self._register_model(obj)

    def _register_model(self, model_class):
        # Generate the _meta automatically (this assumes Neomodel models with properties)
        meta = {
            'label': f"{model_class.__module__}.{model_class.__name__}",
            'db_table': model_class.__name__.lower(),
            'fields': [
                {'name': prop_name, 'db_type': getattr(prop, 'db_property', str(prop))}
                for prop_name, prop in model_class.__all_properties__.items()
            ]
        }
        model_class._meta = meta
        self._models[model_class.__name__] = model_class
        print(f"Registered model: {model_class.__name__}")

    def get_models(self):
        return self._models

# Example usage:
registry = ModelRegistry()
registry.register_models_from_directory('src')

# You can now access the models
all_models = registry.get_models()
print(all_models)