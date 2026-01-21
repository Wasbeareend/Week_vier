import sqlite3

conn = sqlite3.connect("portfolio_opdracht_8_nieuw.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INTEGER PRIMARY KEY,
    wat_te_doen TEXT NOT NULL,
    beschrijving TEXT,
    start_datum TEXT,
    eind_datum TEXT,
    status TEXT,
    device TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS technologies (
    tech_id INTEGER PRIMARY KEY,
    tech_name TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS assignment_technologies (
    assignment_id INTEGER,
    tech_id INTEGER,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
    FOREIGN KEY (tech_id) REFERENCES technologies(tech_id)
)
""")

cursor.execute("""
INSERT OR IGNORE INTO assignments(assignment_id, wat_te_doen, beschrijving, start_datum, eind_datum, status, device)
VALUES(1, 'Portfolio Database', 'SQLite database maken', '2026-01-05', '2026-01-20', 'Bezig', 'Laptop')
""")

cursor.execute("""
INSERT OR IGNORE INTO assignments(assignment_id, wat_te_doen, beschrijving, start_datum, eind_datum, status, device)
VALUES(2, 'Portfolio Website', 'Website bouwen', '2026-01-10', '2026-01-25', 'Starten', 'PC')
""")

cursor.execute("INSERT OR IGNORE INTO technologies(tech_id, tech_name) VALUES(1, 'Python')")
cursor.execute("INSERT OR IGNORE INTO technologies(tech_id, tech_name) VALUES(2, 'SQLite')")
cursor.execute("INSERT OR IGNORE INTO technologies(tech_id, tech_name) VALUES(3, 'HTML')")
cursor.execute("INSERT OR IGNORE INTO technologies(tech_id, tech_name) VALUES(4, 'CSS')")

cursor.execute("INSERT OR IGNORE INTO assignment_technologies(assignment_id, tech_id) VALUES(1, 1)")
cursor.execute("INSERT OR IGNORE INTO assignment_technologies(assignment_id, tech_id) VALUES(1, 2)")
cursor.execute("INSERT OR IGNORE INTO assignment_technologies(assignment_id, tech_id) VALUES(2, 3)")
cursor.execute("INSERT OR IGNORE INTO assignment_technologies(assignment_id, tech_id) VALUES(2, 4)")

conn.commit()
conn.close()
