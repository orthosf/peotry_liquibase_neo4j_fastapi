import os
import inspect
import importlib.util
import sys
from neomodel import StructuredNode, StringProperty, IntegerProperty, StructuredRel
#from django.apps import apps as django_apps

# Function to automatically generate metadata for a model
def generate_meta(model_class):
    label = f'app.{model_class.__name__}'
    db_table = model_class.__name__.lower()

    fields = []
    for name, prop in model_class.__dict__.items():
        if isinstance(prop, (StringProperty, IntegerProperty)):
            db_type = 'varchar(255)' if isinstance(prop, StringProperty) else 'int'
            fields.append({'name': name, 'db_type': db_type})

    return {
        'label': label,
        'db_table': db_table,
        'fields': fields
    }

# Function to discover all models.py files in the project
def discover_model_modules():
    model_modules = []
    for root, dirs, files in os.walk('.'):
        if 'models.py' in files:
            module_name = os.path.relpath(os.path.join(root, 'models.py')).replace('/', '.').replace('\\', '.')[:-3]
            model_modules.append(module_name)
    return model_modules

# Function to import a module from a given module name
def import_module(module_name, imported_modules):
    #print(f"Entered import_module function with: module_name = {module_name}, imported_modules={imported_modules}")
    if module_name in imported_modules:
        #print(f"Module {module_name} already imported.")  # Debug statement
        return sys.modules[module_name]  # Return the already imported module
    #print(f"Importing module: {module_name}")  # Debug statement
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        #print(f"Module {module_name} not found.")  # Debug statement
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.modules[module_name] = module  # Ensure the module is registered in sys.modules
    imported_modules.add(module_name)
    return module

# Function to get all model classes from the discovered model modules
def get_model_classes(imported_modules):
    model_classes = []
    for module_name in discover_model_modules():
        module = import_module(module_name, imported_modules)
        if module:
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and issubclass(obj, StructuredNode) and obj.__module__ == module_name:
                    #print(f"Found model class: {name} in module: {module_name}")  # Debug statement
                    model_classes.append(obj)
                if inspect.isclass(obj) and issubclass(obj, StructuredRel) and obj.__module__ == module_name:
                    #print(f"Found model class: {name} in module: {module_name}")  # Debug statement
                    model_classes.append(obj)    
    return model_classes

# Automatically generate and assign _meta to each model
imported_modules = set()
for model in get_model_classes(imported_modules):
    model._meta = generate_meta(model)

# Registry class to hold models
class MyApp:
    def __init__(self, models):
        self._models = models
    
    def get_models(self):
        return self._models

# Instantiate MyApp with all dynamically loaded models
apps = MyApp(get_model_classes(imported_modules))

print(f"apps: {apps}")
# Example of accessing the generated _meta
for model in apps.get_models():
    print(f"model._meta: {model._meta}")