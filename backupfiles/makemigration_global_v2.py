# src/makemigration.py
import os
import sys
from liquibase_migration_tool.commands.state import StateApps
from liquibase_migration_tool.commands.loader import Loader
from liquibase_migration_tool.commands.autodetector import MigrationAutodetector
from liquibase_migration_tool.commands.writer import MigrationWriter

class Command:
    def handle(self, apps, migrations_dir):
        # Load current model state
        current_state = StateApps.from_apps(apps)

        # Load historical state
        loader = Loader(migrations_dir)
        historical_state = loader.build_graph()

        # Detect changes
        autodetector = MigrationAutodetector(current_state, historical_state)
        changes = autodetector.changes()

        # Generate migration file
        writer = MigrationWriter(changes)
        migration_content = writer.as_string()

        # Write to changelog file
        changelog_file = os.path.join(migrations_dir, 'changelog.xml')
        with open(changelog_file, 'w') as f:
            f.write(migration_content)
        print(f"Migration completed. Changelog written to {changelog_file}")


if __name__ == "__main__":
    command = Command()
    command.handle(apps=sys.modules['your_django_app'], migrations_dir='src/liquibase_migration_tool/migrations/changelogs/')