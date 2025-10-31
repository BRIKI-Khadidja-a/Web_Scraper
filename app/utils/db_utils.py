import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

# Database path
DB_PATH = Path("database/jobs.db")


# data loading functions
# the decorator below tells Streamlit to cache (memorize) the result of this function
@st.cache_data(ttl=3600) 
def load_all_jobs():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM jobs ORDER BY scraped_at DESC"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# retrieve basic statistics about the jobs dataset
@st.cache_data(ttl=3600)
def get_statistics():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = {}
    stats['total_jobs'] = cursor.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    stats['sources'] = cursor.execute("SELECT COUNT(DISTINCT source) FROM jobs").fetchone()[0]
    stats['companies'] = cursor.execute("SELECT COUNT(DISTINCT company) FROM jobs").fetchone()[0]
    stats['locations'] = cursor.execute("SELECT COUNT(DISTINCT location) FROM jobs").fetchone()[0]
    
    conn.close()
    return stats