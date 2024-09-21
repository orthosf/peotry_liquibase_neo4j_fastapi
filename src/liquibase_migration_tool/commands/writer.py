# src/liquibase_migration_tool/commands/writer.py
import uuid
from datetime import datetime
import os

class MigrationWriter:
    def __init__(self, changes):
        self.changes = changes

    def create_statuslog(self, models):
        statuslog = []

        for model in models.values():
            statuslog.append(self._create_model_status(model))

        return statuslog

    def _create_model_status(self, model):
        fields = "\n".join([
            f'<field id="{model._meta["label"]}_fields_{uuid.uuid4()}" name="{field["name"]}" property="{field["db_type"]}" index="False" constrains="True">{field["name"]} = {field["db_type"]}()</field>'
            for field in model._meta['properties']
        ])
        relationships = "\n".join([
            f'<relationship id="{model._meta["label"]}_relationships_{uuid.uuid4()}" name="{rel["name"]}" property="{rel["property"]}" index="False" constrains="True" model="{rel["model"]}">{rel["name"]} = {rel["type"]}("{rel["target"]}", "{rel["name"]}", model={rel["model"]})</relationship>'
            for rel in model._meta.get('relationships', [])
        ])
        return f"""
    <model id="{uuid.uuid4()}" name="{model._meta['label']}" type="StructuredNode">
        <fields id="{model._meta['label']}_fields_{uuid.uuid4()}">
            {fields}
        </fields>
        <relationships id="{model._meta['label']}_relationships_{uuid.uuid4()}">
            {relationships}
        </relationships>
    </model>
    """


    
    def save_changelog(self, migrations_dir):
        
        migration_name = f"changelog_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
        migration_path = os.path.join(migrations_dir, migration_name)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"changelog_{timestamp}.xml"
        filepath = os.path.join(migrations_dir, filename)

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

    def save_statuslog(self, statuslog, migrations_dir):
        statuslog_name = f"statuslog_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
        statuslog_path = os.path.join(migrations_dir, statuslog_name)

        with open(statuslog_path, "w") as file:
            file.write('<databaseStatusLog>\n')
            file.write(f'    <status id="{statuslog_name}" connections="changelog_{datetime.now().strftime("%Y%m%d%H%M%S")}.xml">\n')
            for model_status in statuslog:
                file.write(model_status)
            file.write('    </status>\n')
            file.write('</databaseStatusLog>')

        print(f"Statuslog saved to {statuslog_path}")