import sqlite3
from pathlib import Path

# define path to database 
DB_PATH = Path(__file__).parent.parent / 'database' / 'jobs.db'

   # create jobs table if it doesn't exist
def create_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT NOT NULL,
            date_posted TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


 # insert a job record into the database
def insert_job(job_data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT OR IGNORE INTO jobs (source,title, company, location, date_posted, url)
            VALUES (?,?, ?, ?, ?, ?)
        """, (
            job_data['source'],
            job_data['title'],
            job_data['company'],
            job_data['location'],
            job_data['date_posted'],
            job_data['url']
        ))
        conn.commit()
    except Exception as e:
        print(f"Error inserting job: {e}")
    finally:
        conn.close()
