import sqlite3
import os

DB_PATH = "database/troopod.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        print("Initializing database...")
        conn = get_db_connection()
        with open('database/schema.sql', 'r') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()