class MigrationWriter:
    def __init__(self, changes, output_path):
        self.changes = changes
        self.output_path = output_path

    def write_changelog(self):
        with open(self.output_path, 'w') as f:
            # Write changelog logic
            pass