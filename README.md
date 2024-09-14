# Neo4j-neomodels-FastAPI-Docker-Poetry

##Installation

###To run via docker contrainer
...
docker-compose up
...

###To stop the container
...
docker-compose down
...

python src/liquibase_migration_tool/commands/makemigrations.py migrations
python src/liquibase_migration_tool/commands/makemigrations.py src/liquibase_migration_tool/migrations

...

liquibase update
liquibase update-sql
liquibase releaseLocks
liquibase tag myTag
liquibase tag-exists --tag=myTag
liquibase rollback --tag=myTag


...