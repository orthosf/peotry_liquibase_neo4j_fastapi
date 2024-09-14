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

        # Find the latest changelog file number
        changelog_number = self._get_next_changelog_number(migrations_dir)

        # Write to changelog file with incremented number
        changelog_file = os.path.join(migrations_dir, f'changelog_{changelog_number}.xml')
        with open(changelog_file, 'w') as f:
            f.write(migration_content)
        print(f"Migration completed. Changelog written to {changelog_file}")

    def _get_next_changelog_number(self, migrations_dir):
        # List all files in the migrations directory
        existing_files = os.listdir(migrations_dir)
        changelog_numbers = []

        # Extract numbers from existing changelog files
        for file in existing_files:
            if file.startswith('changelog_') and file.endswith('.xml'):
                try:
                    # Extract the number part of the filename
                    number = int(file[len('changelog_'):-len('.xml')])
                    changelog_numbers.append(number)
                except ValueError:
                    continue

        # Find the next available number
        if changelog_numbers:
            return max(changelog_numbers) + 1
        else:
            return 1  # Start from 1 if no changelog files exist

            
if __name__ == "__main__":
    command = Command()
    command.handle(apps=sys.modules['your_django_app'], migrations_dir='src/liquibase_migration_tool/migrations/changelogs/')