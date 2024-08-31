#!/bin/bash

# Check if the precondition is met (if 'John Doe' exists)
NEO4J_CYPHER_QUERY="MATCH (p:Person {name: 'John Doe'}) RETURN p LIMIT 1"
RESULT=$(cypher-shell -u neo4j -p your_password_here "$NEO4J_CYPHER_QUERY")

if [[ "$RESULT" == *"p"* ]]; then
    echo "Precondition met, executing Liquibase changeset."
    # Run the second changeset
    liquibase --changeLogFile=changelog2.xml update
else
    echo "Precondition not met, skipping Liquibase changeset."
    # Optionally, you could add a loop here to retry after some time
    # sleep 10
    # ./run_liquibase.sh
fi