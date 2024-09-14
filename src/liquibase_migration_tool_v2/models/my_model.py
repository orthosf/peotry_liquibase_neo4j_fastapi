class MyModel:
    class Meta:
        db_table = 'my_model'

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)