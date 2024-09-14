# src/liquibase_migration_tool/commands/state.py

class StateApps:
    def __init__(self, models):
        self.models = models

    @classmethod
    def from_apps(cls, apps):
        models = {}
        for app in apps.get_app_configs():
            for model in app.get_models():
                models[model._meta.label] = model
        print("Models from apps:", models)  # Debug statement
        return cls(models)