-- liquibase formatted cypher

-- changeset your.name:1
CREATE CONSTRAINT FOR (p:Person) REQUIRE p.id IS UNIQUE;
CREATE INDEX FOR (p:Person) ON (p.name);

-- rollback DROP CONSTRAINT ON (p:Person) ASSERT p.id IS UNIQUE;
-- rollback DROP INDEX ON :Person(name);

-- changeset your.name:2
CREATE (p:Person {id: 1, name: 'John Doe', address1: '123 Main St', address2: 'Apt 4B', city: 'Springfield'});
CREATE (p:Person {id: 2, name: 'Jane Doe', address1: '456 Maple Ave', address2: null, city: 'Springfield'});

-- rollback MATCH (p:Person) DETACH DELETE p;

-- changeset your.name:3
CREATE CONSTRAINT FOR (c:Company) REQUIRE c.id IS UNIQUE;
CREATE INDEX FOR (c:Company) ON (c.name);

-- rollback DROP CONSTRAINT ON (c:Company) ASSERT c.id IS UNIQUE;
-- rollback DROP INDEX ON :Company(name);

-- changeset your.name:4
CREATE (c:Company {id: 1, name: 'Acme Corp', address1: '789 Elm St', address2: null, city: 'Metropolis'});
CREATE (c:Company {id: 2, name: 'Globex Corp', address1: '101 Pine Rd', address2: 'Suite 200', city: 'Metropolis'});

-- rollback MATCH (c:Company) DETACH DELETE c;

-- changeset other.dev:5
MATCH (p:Person) SET p.country = 'US';

-- rollback MATCH (p:Person) REMOVE p.country;