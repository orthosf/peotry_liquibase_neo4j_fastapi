import uuid
import os
from datetime import datetime
from state import StateApps  # Ensure StateApps is imported

class MigrationAutodetector:
    def __init__(self, current_state, historical_state):
        #self.current_state = current_state
        #self.historical_state = historical_state
        self.current_state = self._normalize_state(current_state)
        self.historical_state = self._normalize_state(historical_state)

    def _normalize_state(self, state):
        normalized_models = {}
        for label, model in state.models.items():
            normalized_label = label.replace('app.app.', 'app.')
            normalized_models[normalized_label] = model
        return StateApps(normalized_models)

    def changes(self):
        changes = []
        #for label, model in self.current_state.models.items():
            #if label not in self.historical_state.models:
                #changes.append(('create_label', model))
        for model_label, model in self.current_state.models.items():
            #normalized_label = model_label.replace('app.app.', 'app.')
            #if normalized_label not in self.historical_state.models: 
            if model_label not in self.historical_state.models:     
                changes.append(('create_label', model))   
            else:
                #self._detect_property_changes(model, self.historical_state.models[model_label], changes)
                #self._detect_index_changes(model, self.historical_state.models[model_label], changes)
                #self._detect_constraint_changes(model, self.historical_state.models[model_label], changes)
                #self._detect_property_changes(model, self.historical_state.models[model_label], changes)
                #self._detect_index_changes(model, self.historical_state.models[model_label], changes)
                #self._detect_constraint_changes(model, self.historical_state.models[model_label], changes)
                #self._detect_property_changes(model, self.historical_state.models[normalized_label], changes)
                #self._detect_index_changes(model, self.historical_state.models[normalized_label], changes)
                #self._detect_constraint_changes(model, self.historical_state.models[normalized_label], changes)
                self._detect_property_changes(model, self.historical_state.models[model_label], changes)
                self._detect_index_changes(model, self.historical_state.models[model_label], changes)
                self._detect_constraint_changes(model, self.historical_state.models[model_label], changes)
                
        self._detect_removed_labels(changes)
        return changes

    def _detect_property_changes(self, current_model, historical_model, changes):
        #current_properties = {p.name: p for p in current_model._meta['properties']}
        #historical_properties = {p.name: p for p in historical_model._meta['properties']}
        #current_properties = {p['name']: p for p in current_model._meta['properties']}
        #historical_properties = {p['name']: p for p in historical_model._meta['properties']}
        
        current_properties = current_model._meta.get('properties', [])
        historical_properties = historical_model._meta.get('properties', [])

        current_properties_dict = {p['name']: p for p in current_properties}
        historical_properties_dict = {p['name']: p for p in historical_properties}

        for prop_name, prop in current_properties_dict.items():
            if prop_name not in historical_properties_dict:
                changes.append(('add_property', current_model, prop))
            elif prop != historical_properties_dict[prop_name]:
                changes.append(('modify_property', current_model, prop, historical_properties_dict[prop_name]))
        
        for prop_name in historical_properties_dict:
            if prop_name not in current_properties_dict:
                changes.append(('remove_property', current_model, historical_properties_dict[prop_name]))

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
        print(f"self.historical_state.models:{self.historical_state.models}")
        for label in self.historical_state.models:
            print(f"self.current_state.models:{self.current_state.models}")
            print(f"label:{label}")
            #if label not in self.current_state.models:
            #normalized_label = label.replace('app.app.', 'app.')
            #if normalized_label not in self.current_state.models:
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

    def _create_index_changeset(self, model, index):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>CREATE INDEX ON :{model._meta['label']}({index})</cypher>
    </changeSet>
    """

    def _drop_index_changeset(self, model, index):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>DROP INDEX ON :{model._meta['label']}({index})</cypher>
    </changeSet>
    """

    def _create_constraint_changeset(self, model, constraint):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>CREATE CONSTRAINT ON (n:{model._meta['label']}) ASSERT n.{constraint} IS UNIQUE</cypher>
    </changeSet>
    """

    def _drop_constraint_changeset(self, model, constraint):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>DROP CONSTRAINT ON (n:{model._meta['label']}) ASSERT n.{constraint} IS UNIQUE</cypher>
    </changeSet>
    """

    def _remove_label_changeset(self, model):
        return f"""
    <changeSet id="{uuid.uuid4()}" author="liquibase">
        <cypher>MATCH (n:{model._meta['label']})
        DETACH DELETE n</cypher>
    </changeSet>
    """

    def save_changelog(self, changelog, migrations_dir):
        migration_name = f"changelog_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
        migration_path = os.path.join(migrations_dir, migration_name)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"changelog_{timestamp}.xml"
        filepath = os.path.join("migrations", filename)

        with open(filepath, "w") as file:
            file.write("<databaseChangeLog\n")
            file.write('    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"\n')
            file.write('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
            file.write('    xmlns:neo4j="http://www.liquibase.org/xml/ns/neo4j"\n')
            file.write('    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog\n')
            file.write('                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd\n')
            file.write('                        http://www.liquibase.org/xml/ns/neo4j\n')
            file.write('                        http://www.liquibase.org/xml/ns/neo4j/neo4j.xsd">\n')
            for change in changelog:
                file.write(change)
            file.write("\n")
            file.write("</databaseChangeLog>")

        print(f"Changelog saved to {filepath}")