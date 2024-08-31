#!/bin/bash

# Run the first changeset
liquibase --changeLogFile=change_logs4/allchangelog1.xml update

# Execute the custom script to check the precondition and run the second changeset if needed
./run_liquibase.sh