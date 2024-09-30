import os
import inspect
import importlib.util
import sys
from neomodel import StructuredNode, StringProperty, IntegerProperty, StructuredRel, FloatProperty, BooleanProperty, DateTimeProperty, DateProperty, RelationshipTo, RelationshipFrom, UniqueIdProperty
from termcolor import colored
#from django.apps import apps as django_apps

# Function to automatically generate metadata for a model
def generate_meta(model_class):
    label = f'app.{model_class.__name__}'
    db_table = model_class.__name__.lower()

    fields = []
    relationships = []

    for name, prop in model_class.__dict__.items():
        if isinstance(prop, (UniqueIdProperty, StringProperty, IntegerProperty, FloatProperty, BooleanProperty, DateTimeProperty, DateProperty)):
            db_type = 'uuid' if isinstance(prop, UniqueIdProperty) else 'varchar(255)' if isinstance(prop, StringProperty) else 'int' if isinstance(prop, IntegerProperty) else 'float' if isinstance(prop, FloatProperty) else 'boolean' if isinstance(prop, BooleanProperty) else 'datetime' if isinstance(prop, DateTimeProperty) else 'date'
            model_property = 'UniqueIdProperty' if isinstance(prop, UniqueIdProperty) else 'StringProperty(255)' if isinstance(prop, StringProperty) else 'IntegerProperty' if isinstance(prop, IntegerProperty) else 'FloatProperty' if isinstance(prop, FloatProperty) else 'BooleanProperty' if isinstance(prop, BooleanProperty) else 'DateTimeProperty' if isinstance(prop, DateTimeProperty) else 'DateProperty'
            index = getattr(prop, 'index', False)
            constraints = {
                'default': 'auto-generated' if isinstance(prop, UniqueIdProperty) else 'callable' if callable(getattr(prop, 'default', None)) else getattr(prop, 'default', None),
                'unique': getattr(prop, 'unique', False),
                'index': getattr(prop, 'index', False),
                'required': getattr(prop, 'required', False),
                'max_length': getattr(prop, 'max_length', None),
                'min_length': getattr(prop, 'min_length', None),
                'choices': getattr(prop, 'choices', None),
                'lowercase': getattr(prop, 'lowercase', False),
                'uppercase': getattr(prop, 'uppercase', False),
                'regex': getattr(prop, 'regex', None),
                'unique_index': getattr(prop, 'unique_index', False),
                'max_value': getattr(prop, 'max_value', None),
                'min_value': getattr(prop, 'min_value', None)
            }
            fields.append({
                'name': name, 
                'db_type': db_type, 
                "model_property": model_property,
                'index': index,
                'constraints': constraints})
        elif isinstance(prop, (RelationshipTo, RelationshipFrom)):
            relationship = {
                'name': name,
                'type': type(prop).__name__,
                'relation_name': prop.definition.get('relation_type'),
                'direction': prop.definition.get('direction'),
                'model': prop.definition.get('model').__name__ if prop.definition.get('model') else None
            }
            relationships.append(relationship)
    
    model_type = 'StructuredNode' if issubclass(model_class, StructuredNode) else 'StructuredRel' if issubclass(model_class, StructuredRel) else 'Unknown'

    return {
        'label': label,
        'db_table': db_table,
        'fields': fields,
        'relationships': relationships,
        'model_type': model_type
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
        print(f"Module {module_name} not found.")  # Debug statement
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
    #msg = f"model_classes: {model_classes}"
    #print (colored(msg, 'cyan'))                 
    return model_classes

# Automatically generate and assign _meta to each model
imported_modules = set()
for model in get_model_classes(imported_modules):

    model._meta = generate_meta(model)
    #msg = f"model._meta: {model._meta}"
    #print (colored(msg, 'cyan')) 
    #msg = f"Model: {model}"
    #print (colored(msg, 'red'))   

# Registry class to hold models
class MyApp:
    def __init__(self, models):
        self._models = models
    
    def get_models(self):
        return self._models

# Instantiate MyApp with all dynamically loaded models
apps = MyApp(get_model_classes(imported_modules))

#print(f"apps: {apps.get_models}")
# Example of accessing the generated _meta
#for model in apps.get_models():
   # print(f"model._meta: {model._meta}")
   #if issubclass(model, StructuredNode):    #print(f"properties: {class_property}")
        #msg = f"getattibute all propetires: {getattr(model, "__all_properties__")}"
        #print (colored(msg, 'red'))