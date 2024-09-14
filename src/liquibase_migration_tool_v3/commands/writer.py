# src/liquibase_migration_tool/commands/writer.py

class MigrationWriter:
    def __init__(self, changes):
        self.changes = changes

    def as_string(self):
        changelog = "<databaseChangeLog>\n"
        for change in self.changes:
            if change[0] == 'add':
                changelog += f"  <changeSet id=\"{change[1]._meta.label}\" author=\"auto\">\n"
                changelog += f"    <createTable tableName=\"{change[1]._meta.db_table}\">\n"
                for field in change[1]._meta.fields:
                    changelog += f"      <column name=\"{field.name}\" type=\"{field.db_type()}\">\n"
                changelog += "    </createTable>\n"
                changelog += "  </changeSet>\n"
        changelog += "</databaseChangeLog>"
        return changelog