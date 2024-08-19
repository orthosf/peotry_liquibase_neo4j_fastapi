--liquibase formatted cypher

--changeset your.name:1 labels:example-label context:example-context
--comment: Creating person nodes with properties
CREATE CONSTRAINT person_id IF NOT EXISTS ON (p:Person) ASSERT p.id IS UNIQUE;
CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name);
CREATE (p:Person {id: 1, name: 'John Doe', address1: '123 Main St', address2: 'Apt 4B', city: 'Springfield'});
CREATE (p:Person {id: 2, name: 'Jane Doe', address1: '456 Maple Ave', address2: null, city: 'Springfield'});
--rollback MATCH (p:Person) DETACH DELETE p;
--rollback DROP CONSTRAINT person_id;
--rollback DROP INDEX person_name;

--changeset your.name:2 labels:example-label context:example-context
--comment: Creating company nodes with properties
CREATE CONSTRAINT company_id IF NOT EXISTS ON (c:Company) ASSERT c.id IS UNIQUE;
CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name);
CREATE (c:Company {id: 1, name: 'Acme Corp', address1: '789 Elm St', address2: null, city: 'Metropolis'});
CREATE (c:Company {id: 2, name: 'Globex Corp', address1: '101 Pine Rd', address2: 'Suite 200', city: 'Metropolis'});
--rollback MATCH (c:Company) DETACH DELETE c;
--rollback DROP CONSTRAINT company_id;
--rollback DROP INDEX company_name;

--changeset other.dev:3 labels:example-label context:example-context
--comment: Adding country property to person nodes
MATCH (p:Person) SET p.country = 'US';
--rollback MATCH (p:Person) REMOVE p.country;

