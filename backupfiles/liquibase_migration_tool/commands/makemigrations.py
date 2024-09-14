import os
import sys
from datetime import datetime
from autodetector import MigrationAutodetector
from loader import Loader
from state import StateApps
from src.model_registry_global import apps
#from src.liquibase_migration_tool.commands.autodetector import MigrationAutodetector
#from src.liquibase_migration_tool.commands.loader import Loader
#from src.liquibase_migration_tool.commands.state import StateApps
#from src.liquibase_migration_tool.model_registry import apps

def make_migrations(migrations_dir):
    loader = Loader(migrations_dir)
    historical_state = loader.load_historical_state()
    current_state = StateApps.from_apps(apps)

    autodetector = MigrationAutodetector(current_state, historical_state)
    print(f"historical_state: {historical_state}")
    print(f"current_state: {current_state}")
    print(f"autodetector value: {autodetector}")
    changes = autodetector.changes()
    print(f"changes: {changes}")

    if not changes:
        print("No changes detected.")
        return

    changelog = autodetector.create_changelog()
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

    print(f"Created new migration: {migration_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python makemigrations.py <migrations_dir>")
        sys.exit(1)

    migrations_dir = sys.argv[1]
    make_migrations(migrations_dir)