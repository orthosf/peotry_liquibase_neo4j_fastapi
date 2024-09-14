class MigrationAutodetector:
    def __init__(self, current_state, historical_state):
        self.current_state = current_state
        self.historical_state = historical_state

    def changes(self):
        changes = []
        for label, model in self.current_state.models.items():
            if label not in self.historical_state.models:
                changes.append(('create_label', model))
            else:
                self._detect_property_changes(model, self.historical_state.models[label], changes)
                self._detect_index_changes(model, self.historical_state.models[label], changes)
                self._detect_constraint_changes(model, self.historical_state.models[label], changes)
        
        self._detect_removed_labels(changes)
        return changes

    def _detect_property_changes(self, current_model, historical_model, changes):
        current_properties = {p['name']: p for p in current_model._meta['properties']}
        historical_properties = {p['name']: p for p in historical_model._meta['properties']}
        
        for prop_name, prop in current_properties.items():
            if prop_name not in historical_properties:
                changes.append(('add_property', current_model, prop))
            elif prop != historical_properties[prop_name]:
                changes.append(('modify_property', current_model, prop))
        
        for prop_name in historical_properties:
            if prop_name not in current_properties:
                changes.append(('remove_property', current_model, historical_properties[prop_name]))

    def _detect_index_changes(self, current_model, historical_model, changes):
        current_indexes = set(current_model._meta.get('indexes', []))
        historical_indexes = set(historical_model._meta.get('indexes', []))
        
        for index in current_indexes - historical_indexes:
            changes.append(('create_index', current_model, index))
        
        for index in historical_indexes - current_indexes:
            changes.append(('drop_index', current_model, index))

    def _detect_constraint_changes(self, current_model, historical_model, changes):
        current_constraints = set(current_model._meta.get('constraints', []))
        historical_constraints = set(historical_model._meta.get('constraints', []))
        
        for constraint in current_constraints - historical_constraints:
            changes.append(('create_constraint', current_model, constraint))
        
        for constraint in historical_constraints - current_constraints:
            changes.append(('drop_constraint', current_model, constraint))

    def _detect_removed_labels(self, changes):
        for label in self.historical_state.models:
            if label not in self.current_state.models:
                changes.append(('remove_label', self.historical_state.models[label]))