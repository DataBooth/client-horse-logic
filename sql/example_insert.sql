CREATE
OR
REPLACE
TABLE cities (
    name VARCHAR, lat DECIMAL, lon DECIMAL
);

INSERT INTO cities VALUES ('San Francisco', -194.0, 53.0);

CREATE SEQUENCE seq_id START 1;

CREATE
OR
REPLACE
TABLE cities2 (
    id INTEGER PRIMARY KEY, name VARCHAR, lat DECIMAL, lon DECIMAL
);

INSERT INTO cities2 VALUES (nextval('seq_id'), 'San Francisco', -194.0, 53.0);
