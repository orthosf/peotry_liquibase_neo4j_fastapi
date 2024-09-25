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
            normalized_models[normalized_label] = model
        return StateApps(normalized_models)

    """def status(self):
        print(f" --------------- Entered status ---------------------")
        status = []
        for model_label, model in self.current_state.models.items():
            model_status = {
                'label': model_label,
                'meta': model._meta,
                #'attributes': {attr: getattr(model, attr) for attr in dir(model) if not attr.startswith('__') and not callable(getattr(model, attr))},
                #'methods': [method for method in dir(model) if callable(getattr(model, method)) and not method.startswith('__')],
                'is_new': model_label not in self.historical_state.models
            }
            #msg = f"model_status: {model_status}"
            #print(colored(msg, "blue"))   
            status.append(model_status)
        #msg = f"status: {status}"   
        #print(colored(msg, "yellow"))        
        return status"""

    def status(self):
        print(f" --------------- Entered status ---------------------")
        status = []
        for model_label, model in self.current_state.models.items():
            if model_label not in self.historical_statuslog.models:
                model_status = {
                    'label': model_label,
                    'meta': model._meta,
                    'is_new': True
                    'status': "new"
                }
                status.append(model_status)
        # Detect removed labels
        self._detect_removed_labels_status(status)  
              
        return status


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

    def _detect_removed_labels_status(self, status):
    for label in self.historical_state.models:
        if label not in self.current_state.models:
            model_status = {
                'label': label,
                'meta': self.historical_state.models[label]._meta,
                'is_removed': True
                'status': "remove"
            }
            status.append(model_status)


    def _detect_property_changes(self, current_model, historical_model, changes):       
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
        print(f" --------------- Entered Create_status ---------------------")
        status = self.status()

        if status:
            statuslog = []
            msg = f'statuslog:{statuslog}'
            print(colored(msg, "cyan"))
            for model_status in status:
                fields = "\n".join([
                    f'''                        <field id="{model_status["label"]}_fields_{uuid.uuid4()}" name="{field["name"]}" property="{field["instance"]}" index="{field["index"]}" status="new" change="bde3b2a1-fa33-4185-9ae6-f84d3627051c">
                            {field["name"]} = {field["instance"]}()
                            <constraints>
{self._format_constraints(field["constraints"], indent_level=8)}
                            </constraints>
                        </field>'''
                    for field in model_status['meta']['fields']
                ])
                relationships = "\n".join([
                    f'                        <relationship id="{model_status["label"]}_relationships_{uuid.uuid4()}" name="{rel["name"]}" property="{rel["type"]}" model="{rel["model"]}" relation_name="{rel["relation_name"]}" direction="{rel["direction"]}">{rel["name"]} = {rel["type"]}("{rel["relation_name"]}" "{rel["name"]}" model={rel["model"]})</relationship>'
                    for rel in model_status['meta'].get('relationships', [])
                ])
                statuslog.append(f"""
                    <model id="{uuid.uuid4()}" name="{model_status['label']}" type="StructuredNode">
                        <fields id="{model_status['label']}_fields_{uuid.uuid4()}">
{fields}
                        </fields>
                        <relationships id="{model_status['label']}_relationships_{uuid.uuid4()}">
{relationships}
                        </relationships>
                        <is_new>{model_status['is_new']}</is_new>
                        

                    </model>
""")
            msg = f'statuslog:{statuslog}'
            print(colored(msg, "yellow"))
            return statuslog
        else:
            statuslog = []
            #msg = "No status changes detected."
            #print(colored(msg, "red"))
            #msg = f'statuslog:{statuslog}'
            #print(colored(msg, "yellow"))
            return statuslog

    def save_statuslog(self, statuslog, migrations_dir):
        if not statuslog:
            msg = f'statuslog:{statuslog}'
            print(colored(msg, "yellow"))
            msg = "No status changes detected."
            print(colored(msg, "red"))
            return
        else:
            print("Status changes detected") 
            msg = f'statuslog:{statuslog}'
            print(colored(msg, "yellow"))  
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

    def _format_constraints(self, constraints, indent_level=0):
        indent = ' ' * indent_level
        inner_indent = ' ' * (indent_level + 7)
        formatted_constraints = []
        for key, value in constraints.items():
            if key == "choices" and isinstance(value, dict):
                choices = "\n".join([
                    f'                                    <choice id="choice_{i}" name="{html.escape(str(k))}">{html.escape(str(v))}</choice>'
                    for i, (k, v) in enumerate(value.items(), 1)
                ])
                formatted_constraints.append(f'                                <constraint name="{key}">\n{choices}\n{indent}                        </constraint>')
            else:
                formatted_constraints.append(f'                                <constraint name="{key}">{self._format_constraint_value(value)}</constraint>')
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