import sqlite3
from itertools import groupby

class Database:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        # Establishes a connection to the SQLite database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Sets the row_factory to retrieve rows as dictionaries
        return conn

    def get_numberPlates(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Executes a SELECT query to retrieve all rows from the "numberplates" table
            cursor.execute("SELECT * FROM numberplates")
            return cursor.fetchall()  # Returns all fetched rows as a list of dictionaries

    def add_numberPlates(self, plate):
        with self.get_connection() as conn:
            # Executes an INSERT query to add a new number plate to the "numberplates" table
            conn.execute("INSERT INTO numberplates (plate) VALUES (?)", (plate,))