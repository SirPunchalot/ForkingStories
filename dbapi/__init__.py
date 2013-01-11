import sqlite3
import os.path

# This is the directory of this file
db_path = os.path.dirname(__file__)

conn = sqlite3.connect(db_path + "/database.db")
cur = conn.cursor()
cur.executescript(open(db_path + "/setup.sql").read())
