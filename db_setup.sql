
DROP TABLE IF EXISTS registrations;
CREATE TABLE registrations (
    date TEXT NOT NULL,
    state TEXT NOT NULL,
    vehicle_class TEXT NOT NULL,
    manufacturer TEXT NOT NULL,
    registrations INTEGER NOT NULL
);
-- Use SQLite CLI or etl.py to import CSV.
