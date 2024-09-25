import os
import sys
from datetime import datetime
from autodetector import MigrationAutodetector
from loader import Loader
from state import StateApps
from src.model_registry_global import apps
from termcolor import colored
from statuslogLoader import StatuslogLoader

def make_migrations(migrations_dir):
    loader = Loader(migrations_dir)
    historical_state = loader.load_historical_state()
    statuslog_loader = StatuslogLoader(migrations_dir)
    historical_statuslog = statuslog_loader.load_historical_statuslog()
    current_state = StateApps.from_apps(apps)
    autodetector = MigrationAutodetector(current_state, historical_state, migrations_dir, historical_statuslog)
    changes = autodetector.changes()
    status = autodetector.status()
    print("Logging current state:")
    #current_state.log_contents()

    msg = f"current_state.items() ---- {dir(current_state)}"
    print(colored(msg, "magenta"))

    """
    for attr_name, attr_value in current_state.__dict__.items():
        #if not attr_name.startswith('__'):
        msg = f"current_state.__dict__.items ----  {attr_name}: {attr_value}"
        print(colored(msg, "red"))
    for attr_name, attr_value in current_state.models.items():    
        msg = f"current_state.models.items ---- {attr_name}: {attr_value}"
        print(colored(msg, "cyan"))"""

    statuslog = autodetector.create_statuslog()
    autodetector.save_statuslog(statuslog, migrations_dir)
    #msg = f"statuslog: {statuslog}"
    #print(colored(msg, "red"))  
    if not changes:
        print("No changes detected.")
        return
    else:
        print("Changes detected")   

    changelog = autodetector.create_changelog()
    autodetector.save_changelog(changelog, migrations_dir)
    msg = f"changes: {changes}" 
    print(colored(msg, 'yellow'))    
    


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python makemigrations.py <migrations_dir>")
        sys.exit(1)

    migrations_dir = sys.argv[1]
    make_migrations(migrations_dir)