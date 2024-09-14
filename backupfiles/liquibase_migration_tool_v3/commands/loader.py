# src/liquibase_migration_tool/commands/loader.py
import os

class Loader:
    def __init__(self, migrations_dir):
        self.migrations_dir = migrations_dir

    def build_graph(self):
        graph = {}
        for filename in os.listdir(self.migrations_dir):
            if filename.endswith('.xml'):
                # Here you can parse the Liquibase XML files to build the migration graph.
                pass
        return graph