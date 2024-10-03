# src/liquibase_migration_tool/commands/state.py

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

    def to_statuslog_format(self):
        statuslog = []
        for label, model in self.models.items():
            statuslog.append({
                'label': label,
                'properties': model._meta['properties']
            })
        return statuslog