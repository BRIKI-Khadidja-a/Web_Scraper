import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# create Supabase client 
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#insert a job record into the database
def insert_job(job_data):
    data = {
        "source": job_data["source"],
        "title": job_data["title"],
        "company": job_data["company"],
        "location": job_data["location"],
        "date_posted": job_data["date_posted"],
        "url": job_data["url"]
    }

    supabase.table("jobs").insert(data).execute()

  
