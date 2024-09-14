import os
from datetime import datetime
from .autodetector import MigrationAutodetector
from .loader import Loader
from .state import StateApps
from ..model_registry import apps

def make_migrations(migrations_dir):
    loader = Loader(migrations_dir)
    historical_state = loader.load_historical_state()
    current_state = StateApps.from_apps(apps)

    autodetector = MigrationAutodetector(current_state, historical_state)
    changes = autodetector.changes()

    if not changes:
        print("No changes detected.")
        return

    changelog = autodetector.create_changelog()
    migration_name = f"changelog_{datetime.now().strftime('%Y%m%d%H%M%S')}.xml"
    migration_path = os.path.join(migrations_dir, migration_name)

    with open(migration_path, 'w') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<databaseChangeLog\n')
        f.write('    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"\n')
        f.write('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n')
        f.write('    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog\n')
        f.write('    http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.1.xsd">\n')
        f.write('\n'.join(changelog))
        f.write('</databaseChangeLog>\n')

    print(f"Created new migration: {migration_path}")