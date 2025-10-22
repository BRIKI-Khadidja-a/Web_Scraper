#utility script to display all jobs stored in the local database it is used for quick manual testing


import sqlite3
from database.db import insert_job

# connect to your database file
conn = sqlite3.connect('database/jobs.db')
cursor = conn.cursor()

# fetch and display all rows
cursor.execute("SELECT * FROM jobs")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()