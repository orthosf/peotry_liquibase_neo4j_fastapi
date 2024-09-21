# src/liquibase_migration_tool/commands/writer.py
class MigrationWriter:
    def __init__(self, changes):
        self.changes = changes

    def as_string(self):
        changelog = '<?xml version="1.0" encoding="UTF-8"?>\n'
        changelog += '<databaseChangeLog\n'
        changelog += '    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"\n'
        changelog += '    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
        changelog += '    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog\n'
        changelog += '                        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.8.xsd">\n\n'

        for change in self.changes:
            if change[0] == 'add_table':
                changelog += self._create_table(change[1])
            elif change[0] == 'add_column':
                changelog += self._add_column(change[1], change[2])
            elif change[0] == 'modify_column':
                changelog += self._modify_column(change[1], change[2])
            elif change[0] == 'remove_column':
                changelog += self._remove_column(change[1], change[2])

        changelog += '</databaseChangeLog>'
        return changelog

    def _create_table(self, model):
        changeset = f'  <changeSet id="create-{model._meta["db_table"]}" author="auto">\n'
        changeset += f'    <createTable tableName="{model._meta["db_table"]}">\n'
        for field in model._meta['fields']:
            changeset += f'      <column name="{field["name"]}" type="{field["db_type"]}">\n'
            changeset += '        <constraints nullable="true"/>\n'
            changeset += '      </column>\n'
        changeset += '    </createTable>\n'
        changeset += '  </changeSet>\n\n'
        return changeset

    def _add_column(self, model, field):
        changeset = f'  <changeSet id="add-column-{model._meta["db_table"]}-{field["name"]}" author="auto">\n'
        changeset += f'    <addColumn tableName="{model._meta["db_table"]}">\n'
        changeset += f'      <column name="{field["name"]}" type="{field["db_type"]}">\n'
        changeset += '        <constraints nullable="true"/>\n'
        changeset += '      </column>\n'
        changeset += '    </addColumn>\n'
        changeset += '  </changeSet>\n\n'
        return changeset

    def _modify_column(self, model, field):
        changeset = f'  <changeSet id="modify-column-{model._meta["db_table"]}-{field["name"]}" author="auto">\n'
        changeset += f'    <modifyDataType tableName="{model._meta["db_table"]}" columnName="{field["name"]}" newDataType="{field["db_type"]}"/>\n'
        changeset += '  </changeSet>\n\n'
        return changeset

    def _remove_column(self, model, field):
        changeset = f'  <changeSet id="remove-column-{model._meta["db_table"]}-{field["name"]}" author="auto">\n'
        changeset += f'    <dropColumn tableName="{model._meta["db_table"]}" columnName="{field["name"]}"/>\n'
        changeset += '  </changeSet>\n\n'
        return changeset