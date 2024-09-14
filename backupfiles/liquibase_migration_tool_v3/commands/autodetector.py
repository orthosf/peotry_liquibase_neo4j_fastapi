# src/liquibase_migration_tool/commands/autodetector.py

class MigrationAutodetector:
    def __init__(self, current_state, historical_state):
        self.current_state = current_state
        self.historical_state = historical_state

    def changes(self):
        changes = []
        for model_label, model in self.current_state.models.items():
            if model_label not in self.historical_state:
                changes.append(('add', model))
            # Add more logic to compare fields, relationships, etc.
        return changes