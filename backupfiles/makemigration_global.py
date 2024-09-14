# src/makemigration.py
import os
import sys
from liquibase_migration_tool.commands.state import StateApps
from liquibase_migration_tool.commands.loader import Loader
from liquibase_migration_tool.commands.autodetector import MigrationAutodetector
from liquibase_migration_tool.commands.writer import MigrationWriter

class Command:
    def handle(self, apps, migrations_dir):
        # ... existing code ...

        # Generate migration file
        writer = MigrationWriter(changes)
        migration_content = writer.as_string()

        # Find the latest changelog file number
        changelog_number = self._get_next_changelog_number(migrations_dir)

        # Write to changelog file with incremented number
        changelog_file = os.path.join(migrations_dir, f'changelog_{changelog_number:04d}.xml')
        with open(changelog_file, 'w') as f:
            f.write(migration_content)
        print(f"Migration completed. Changelog written to {changelog_file}")

    # ... existing code ...

if __name__ == "__main__":
    from model_registry import apps
    command = Command()
    command.handle(apps=apps, migrations_dir='src/liquibase_migration_tool/migrations/changelogs/')