from commands.make_migration import MakeMigrationCommand
from models import all_models

if __name__ == '__main__':
    MakeMigrationCommand(all_models, 'migrations/changelogs/', 'new_changelog.xml').handle()