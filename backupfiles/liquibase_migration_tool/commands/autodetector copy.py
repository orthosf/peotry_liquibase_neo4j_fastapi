class MigrationAutodetector:
    def __init__(self, current_state, historical_state):
        self.current_state = current_state
        self.historical_state = historical_state

    def changes(self):
        changes = []
        for model_label, model in self.current_state.models.items():
            if model_label not in self.historical_state:
                changes.append(('add_table', model))
            else:
                # Compare fields
                current_fields = {f['name']: f for f in model._meta['fields']}
                historical_fields = {f['name']: f for f in self.historical_state[model_label]._meta['fields']}
                
                for field_name, field in current_fields.items():
                    if field_name not in historical_fields:
                        changes.append(('add_column', model, field))
                    elif field != historical_fields[field_name]:
                        changes.append(('modify_column', model, field))
                
                for field_name in historical_fields:
                    if field_name not in current_fields:
                        changes.append(('remove_column', model, historical_fields[field_name]))
        
        return changes