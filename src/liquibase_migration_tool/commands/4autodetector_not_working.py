import uuid
import os
from datetime import datetime
from state import StateApps  # Ensure StateApps is imported
from termcolor import colored
import html


class MigrationAutodetector:
    def __init__(self, current_state, historical_state, migrations_dir, historical_statuslog):
        self.current_state = self._normalize_state(current_state)
        self.historical_state = self._normalize_state(historical_state)
        self.migrations_dir = migrations_dir
        self.historical_statuslog = historical_statuslog

    def _normalize_state(self, state):
        normalized_models = {}
        for label, model in state.models.items():
            normalized_label = label.replace('app.app.', 'app.')
            normalized_fields = []
            for field in model._meta.get('fields', []):
                normalized_field = {
                    'name': field['name'],
                    'property': field['instance'].__class__.__name__,
                    'index': str(field['index']),
                    'constraints': field.get('constraints', {})
                }
                normalized_fields.append(normalized_field)
            normalized_models[normalized_label] = {
                '_meta': {
                    'fields': normalized_fields,
                    'properties': model._meta.get('properties', []),
                    'indexes': model._meta.get('indexes', []),
                    'constraints': model._meta.get('constraints', []),
                }
            }
        return StateApps(normalized_models)

    def status(self):
        print(f" --------------- Entered status ---------------------")
        status = []
        for model_label, model in self.current_state.models.items():
            if model_label not in self.historical_statuslog.models:
                msg = f'model_label:{model_label}'
                print(colored(msg, "red"))
                model_status = {
                    'label': model_label,
                    'meta': {
                        'model_type': model._meta.get('model_type', 'StructuredNode'),
                        'fields': model._meta.get('fields', []),
                        'properties': model._meta.get('properties', []),
                        'indexes': model._meta.get('indexes', []),
                        'constraints': model._meta.get('constraints', []),
                    },
                    'status': "new"
                }
                status.append(model_status)
            else:
                model_status = {
                    'label': model_label,
                    'meta': {
                        'model_type': model._meta.get('model_type', 'StructuredNode'),
                        'fields': [],  # Initialize with an empty list
                        'properties': model._meta.get('properties', []),
                        'indexes': model._meta.get('indexes', []),
                        'constraints': model._meta.get('constraints', []),
                    },
                    'status': "update"
                }
                self._detect_field_status_changes(model, self.historical_statuslog.models[model_label], model_status)
                if 'field_changes' in model_status:
                    print(f"model_status:{model_status}")
                    status.append(model_status)

        # Detect removed labels 
        self._detect_removed_labels_status(status)        
        return status

    def _detect_field_status_changes(self, current_model, historical_model, model_status):
        current_fields = {field['name']: field for field in current_model._meta.get('fields', [])}
        msg = f"current_fields:{current_fields}"
        print(colored(msg, "cyan"))
        historical_fields = {field['name']: field for field in historical_model._meta.get('fields', [])}
        msg = f"historical_fields:{historical_fields}"
        print(colored(msg, "magenta"))
        added_fields = []
        removed_fields = []
        modified_fields = []

        for field_name in historical_fields:
            if field_name not in current_fields:
                removed_fields.append(historical_fields[field_name])
                model_status.setdefault('field_changes', []).append(('remove_field', historical_fields[field_name]))
                msg = f"remove_field:{historical_fields[field_name]}"
                print(colored(msg, "red"))

        for field_name, field in current_fields.items():
            if field_name not in historical_fields:
                added_fields.append(field)
                model_status.setdefault('field_changes', []).append(('add_field', field))
                msg = f"add_field:{field}"
                print(colored(msg, "red"))
            else:
                current_field = field
                historical_field = historical_fields[field_name]
                if not self._compare_fields(current_field, historical_field):
                    modified_fields.append(current_field)
                    model_status.setdefault('field_changes', []).append(('modify_field', current_field, historical_field))
                    msg = f"modify_field:{current_field}"
                    print(colored(msg, "red"))

        model_status['meta']['fields'] = added_fields + removed_fields + modified_fields

    def _compare_fields(self, current_field, historical_field):
        # Normalize field types
        current_field_type = current_field['db_type']
        historical_field_type = historical_field.get('property')

        # Compare field properties
        if current_field_type != historical_field_type:
            msg = f"Field type mismatch: {current_field_type} != {historical_field_type}"
            print(colored(msg, "yellow"))
            return False
        if current_field['index'] != (historical_field.get('index') == 'True'):
            msg = f"Field index mismatch: {current_field['index']} != {(historical_field.get('index') == 'True')}"
            print(colored(msg, "yellow"))
            return False

        # Compare constraints
        current_constraints = self._serialize_constraints(current_field['constraints'])
        historical_constraints = self._serialize_constraints(historical_field.get('constraints', {}))
        if current_constraints != historical_constraints:
            msg = f"Constraints mismatch: {current_constraints} != {historical_constraints}"
            print(colored(msg, "red"))
            return False

        return True

    def _serialize_constraints(self, constraints):
        # Serialize constraints to a comparable format
        serialized = {}
        for key, value in constraints.items():
            if callable(value):
                serialized[key] = 'callable'
            elif value is None:
                serialized[key] = 'null'
            elif isinstance(value, bool):
                serialized[key] = str(value).lower()
            elif isinstance(value, (int, float)):
                serialized[key] = str(value)
            else:
                serialized[key] = str(value)
        return serialized

    def changes(self):
        changes = []
        for model_label, model in self.current_state.models.items():
            if model_label not in self.historical_state.models:     
                changes.append(('create_label', model))   
            else:
                self._detect_property_changes(model, self.historical_state.models[model_label], changes)
                self._detect_index_changes(model, self.historical_state.models[model_label], changes)
                self._detect_constraint_changes(model, self.historical_state.models[model_label], changes)
                
        self._detect_removed_labels(changes)
        return changes

    def _detect_property_changes(self, current_model, historical_model, changes):
        current_properties = current_model.get('_meta', {}).get('properties', [])
        historical_properties = historical_model.get('_meta', {}).get('properties', [])
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
       # print(f"self.historical_state.models:{self.historical_state.models}")
        for label in self.historical_state.models:
            #print(f"self.current_state.models:{self.current_state.models}")
            #print(f"label:{label}")
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

    def save_changelog(self, changelog, migrations_dir):
        migration_name = f"changelog_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
        migration_path = os.path.join(migrations_dir, migration_name)
        #autodetector.save_changelog(changelog)
        with open(migration_path, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<databaseChangeLog\n')
            f.write('    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"\n')
            f.write('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
            f.write('    xmlns:neo4j="http://www.liquibase.org/xml/ns/neo4j"\n')
            f.write('    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog\n')
            f.write('                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd\n')
            f.write('                        http://www.liquibase.org/xml/ns/neo4j\n')
            f.write('                        http://www.liquibase.org/xml/ns/neo4j/neo4j.xsd">\n')
            f.write('\n'.join(changelog))
            f.write('</databaseChangeLog>\n')

        msg = f"Created new migration: {migration_path}"
        print(colored(msg, "green"))

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

    def create_statuslog(self):
        status = self.status()
        if status:
            statuslog = []
            for model_status in status:
                fields = self._format_fields(model_status['meta']['fields'])
                relationships = self._format_relationships(model_status['meta'].get('relationships', []))
                statuslog.append(f"""
                    <model id="{uuid.uuid4()}" name="{model_status['label']}" type="{model_status['meta']['model_type']}" status="{model_status['status']}" >
                        <fields id="{model_status['label']}_fields_{uuid.uuid4()}">
{fields}
                        </fields>
                        <relationships id="{model_status['label']}_relationships_{uuid.uuid4()}">
{relationships}
                        </relationships>
                        <status>{model_status['status']}</status>
                    </model>
                """)
            msg = 'statuslog detected'
            print(colored(msg, "yellow"))
            return statuslog
        else:
            statuslog = []
            return statuslog

    def save_statuslog(self, statuslog, migrations_dir):
        if not statuslog:
            msg = f'statuslog:{statuslog}'
            print(colored(msg, "yellow"))
            msg = "No status changes detected."
            print(colored(msg, "red"))
            return
        else:
            statuslog_name = f"statuslog_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
            statuslog_path = os.path.join(migrations_dir, statuslog_name)

            with open(statuslog_path, "w") as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write('<databaseStatusLog>\n')
                file.write(f'    <status id="{statuslog_name}" connections="changelog_{datetime.now().strftime("%Y%m%d%H%M%S")}.xml">\n')
                for model_status in statuslog:
                    file.write(model_status)
                file.write('    </status>\n')
                file.write('</databaseStatusLog>')
            msg = f"Statuslog saved to {statuslog_path}"
            print(colored(msg, "green"))

    def _format_fields(self, fields):
        formatted_fields = []
        for field in fields:
            constraints = self._format_constraints(field.get('constraints', {}))
            formatted_fields.append(f"""
                        <field id="{field['name']}" name="{field['name']}" property="{field['instance']}" index="{field['index']}" status="new" change="bde3b2a1-fa33-4185-9ae6-f84d3627051c">
                            {field['name']} = {field['instance']}()
                            <constraints>
{constraints}
                            </constraints>
                        </field>
            """)
        return "\n".join(formatted_fields)

    def _format_relationships(self, relationships):
        formatted_relationships = []
        for rel in relationships:
            formatted_relationships.append(f"""
                        <relationship id="{rel['name']}" name="{rel['name']}" property="{rel['type']}" model="{rel['model']}" relation_name="{rel['relation_name']}" direction="{rel['direction']}" status="new" change="bde3b2a1-fa33-4185-9ae6-f84d3627051c">{rel['name']} = {rel['type']}("{rel['relation_name']}" "{rel['name']}" model={rel['model']})</relationship>
            """)
        return "\n".join(formatted_relationships)

    def _format_constraints(self, constraints):
        formatted_constraints = []
        for key, value in constraints.items():
            if key == "choices" and isinstance(value, dict):
                choices = "\n".join([
                    f'                                    <choice id="choice_{i}" name="{html.escape(str(k))}" value="{html.escape(str(v))}"></choice>'
                    for i, (k, v) in enumerate(value.items(), 1)
                ])
                formatted_constraints.append(f'                                <constraint name="{key}" status="new" change="bde3b2a1-fa33-4185-9ae6-f84d3627051c">\n{choices}\n                                </constraint>')
            else:
                formatted_constraints.append(f'                                <constraint name="{key}" status="new" change="bde3b2a1-fa33-4185-9ae6-f84d3627051c" value = "{self._format_constraint_value(value)}"></constraint>')
        return "\n".join(formatted_constraints) 

    def _format_constraint_value(self, value):
        if callable(value):
            return "callable"
        elif value is None:
            return "null"
        elif isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, (int, float)):
            return str(value)
        else:
            return html.escape(str(value))