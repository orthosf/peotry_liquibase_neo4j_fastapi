import uuid
from datetime import datetime

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
                changes.append(('modify_property', current_model, prop, historical_properties[prop_name]))
        
        for prop_name in historical_properties:
            if prop_name not in current_properties:
                changes.append(('remove_property', current_model, historical_properties[prop_name]))

    # ... (keep _detect_index_changes and _detect_constraint_changes as they are)

    def _detect_removed_labels(self, changes):
        for label in self.historical_state.models:
            if label not in self.current_state.models:
                changes.append(('remove_label', self.historical_state.models[label]))

    def create_changelog(self):
        changes = self.changes()
        changelog = []
        
        for change in changes:
            if change[0] == 'create_label':
                changelog.append(self._create_label_changeset(change[1]))
            elif change[0] == 'add_property':
                changelog.append(self._add_property_changeset(change[1], change[2]))
            elif change[0] == 'modify_property':
                changelog.append(self._modify_property_changeset(change[1], change[2], change[3]))
            elif change[0] == 'remove_property':
                changelog.append(self._remove_property_changeset(change[1], change[2]))
            elif change[0] == 'create_index':
                changelog.append(self._create_index_changeset(change[1], change[2]))
            elif change[0] == 'drop_index':
                changelog.append(self._drop_index_changeset(change[1], change[2]))
            elif change[0] == 'create_constraint':
                changelog.append(self._create_constraint_changeset(change[1], change[2]))
            elif change[0] == 'drop_constraint':
                changelog.append(self._drop_constraint_changeset(change[1], change[2]))
            elif change[0] == 'remove_label':
                changelog.append(self._remove_label_changeset(change[1]))

        return changelog

    def _create_label_changeset(self, model):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>CREATE (:{model._meta['label']})</cypher>
    </changeSet>
    """

    def _add_property_changeset(self, model, property):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>MATCH (n:{model._meta['label']})
SET n.{property['name']} = null
RETURN n</cypher>
    </changeSet>
    """

    def _modify_property_changeset(self, model, new_property, old_property):
        # For Neo4j, modifying a property is the same as adding it
        return self._add_property_changeset(model, new_property)

    def _remove_property_changeset(self, model, property):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>MATCH (n:{model._meta['label']})
REMOVE n.{property['name']}
RETURN n</cypher>
    </changeSet>
    """

    # ... (implement _create_index_changeset, _drop_index_changeset, _create_constraint_changeset, _drop_constraint_changeset)

    def _remove_label_changeset(self, model):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>MATCH (n:{model._meta['label']})
DETACH DELETE n</cypher>
    </changeSet>
    """