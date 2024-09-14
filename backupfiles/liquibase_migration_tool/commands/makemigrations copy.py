import os
from datetime import datetime
from .state import StateApps
from .autodetector import MigrationAutodetector
from .writer import MigrationWriter
from .loader import Loader

def makemigrations(apps, migrations_dir):
    # Create migrations directory if it doesn't exist
    os.makedirs(migrations_dir, exist_ok=True)

    # Get current state
    current_state = StateApps.from_apps(apps)

    # Load historical state
    loader = Loader(migrations_dir)
    historical_state = loader.load_historical_state()

    # Detect changes
    autodetector = MigrationAutodetector(current_state, historical_state)
    changes = autodetector.changes()

    if not changes:
        print("No changes detected.")
        return

    # Generate migration content
    writer = MigrationWriter(changes)
    migration_content = writer.as_string()

    # Create new migration file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{timestamp}_auto_generated.xml"
    file_path = os.path.join(migrations_dir, filename)

    with open(file_path, 'w') as f:
        f.write(migration_content)

    print(f"Created new migration: {file_path}")