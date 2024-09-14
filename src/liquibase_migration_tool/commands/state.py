# src/liquibase_migration_tool/commands/state.py

class StateApps:
    def __init__(self, models):
        self.models = models

    @classmethod
    def from_apps(cls, apps):
        models = {}
        for model in apps.get_models():
            models[model._meta['label']] = model
        #print("Models from apps:", models)  # Debug statement
        return cls(models)