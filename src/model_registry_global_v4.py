# models_registry.py

import inspect
import models  # Import the models module where all model classes are defined
from neomodel import StructuredNode, StringProperty, IntegerProperty

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

# Get all model classes from the models module
def get_model_classes():
    model_classes = []
    for name, obj in inspect.getmembers(models):
        if inspect.isclass(obj) and issubclass(obj, StructuredNode) and obj.__module__ == 'models':
            model_classes.append(obj)
    return model_classes

# Automatically generate and assign _meta to each model
for model in get_model_classes():
    model._meta = generate_meta(model)

# Registry class to hold models
class MyApp:
    def __init__(self, models):
        self._models = models
    
    def get_models(self):
        return self._models

# Instantiate MyApp with all dynamically loaded models
apps = MyApp(get_model_classes())

# Example of accessing the generated _meta
for model in apps.get_models():
    print(model._meta)