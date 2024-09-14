class MakeMigrationCommand:
    def __init__(self, models, changelog_path, output_path):
        self.models = models
        self.changelog_path = changelog_path
        self.output_path = output_path

    def handle(self):
        # Command logic to run migrations
        pass