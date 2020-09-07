import sqlite3
conn = sqlite3.connect("password-manager.db")
c = conn.cursor()
c.execute("PRAGMA foreign_keys = ON")
