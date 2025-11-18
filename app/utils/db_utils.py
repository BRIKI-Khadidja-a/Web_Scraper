import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# create the client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# data loading functions
@st.cache_data(ttl=3600)# the decorator tells Streamlit to cache the result of this function
def load_all_jobs():
    response = supabase.table('jobs').select('*').order('scraped_at', desc=True).execute()
    df = pd.DataFrame(response.data)
    return df


@st.cache_data(ttl=3600)
def get_statistics():
    stats = {}
    
    # jobs count
    total_response = supabase.table('jobs').select('*', count='exact').execute()
    stats['total_jobs'] = total_response.count
    
    # sources count
    sources_response = supabase.table('jobs').select('source').execute()
    stats['sources'] = pd.DataFrame(sources_response.data)['source'].nunique()
    
    # companies count
    companies_response = supabase.table('jobs').select('company').execute()
    stats['companies'] = pd.DataFrame(companies_response.data)['company'].nunique()
    
    # locations count
    locations_response = supabase.table('jobs').select('location').execute()
    stats['locations'] = pd.DataFrame(locations_response.data)['location'].nunique()
    
    return stats