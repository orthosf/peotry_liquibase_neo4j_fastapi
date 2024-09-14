"""Migration script to generate changelog.xml."""
from liquibase_migration_tool_v2.commands.make_migration import MakeMigrationCommand
from liquibase_migration_tool_v2.models import all_models

import os

# Define the output file path for the changelog
output_dir = "src/liquibase_migration_tool/migrations/changelogs/"
output_file = os.path.join(output_dir, "changelog.xml")

if __name__ == "__main__":
    try:
        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Run the migration tool to generate the changelog.xml file
        MakeMigrationCommand(
            all_models,
            output_dir,
            output_file
        ).handle()

        print(f"Migration completed successfully. Changelog generated at {output_file}")

    except Exception as exc:
        print(f"Error: {exc}")
        print("Migration failed")