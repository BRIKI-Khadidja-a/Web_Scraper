import streamlit as st
from utils.db_utils import load_all_jobs
import pandas as pd

# Sets page title and icon
st.set_page_config(page_title="Browse Jobs", page_icon="📊", layout="wide")

# Title
st.title("📊 Browse Job Opportunities")
st.write("Explore all available cybersecurity job listings from multiple sources.")
st.divider()

# Load all jobs
with st.spinner("Loading job listings..."):
    df = load_all_jobs()

# Check if data is available
if df.empty:
    st.warning("⚠️ No job data available. The database might be empty.")
    st.info("💡 Run the scrapers to collect job listings first.")
else:
    # Filters sidebar
    st.sidebar.header("🔍 Filters")
    
    # Source filter
    sources = ['All'] + sorted(df['source'].unique().tolist())
    selected_source = st.sidebar.selectbox("Data Source", sources)
    
    # Company filter
    companies = ['All'] + sorted(df['company'].unique().tolist())
    selected_company = st.sidebar.selectbox("Company", companies)
    
    # Location filter
    locations = ['All'] + sorted(df['location'].unique().tolist())
    selected_location = st.sidebar.selectbox("Location", locations)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['source'] == selected_source]
    
    if selected_company != 'All':
        filtered_df = filtered_df[filtered_df['company'] == selected_company]
    
    if selected_location != 'All':
        filtered_df = filtered_df[filtered_df['location'] == selected_location]
    
    # Sort options
    st.sidebar.divider()
    st.sidebar.header("📋 Sort Options")
    sort_by = st.sidebar.selectbox(
        "Sort by",
        ["Most Recent", "Company", "Location", "Source"]
    )
    
    if sort_by == "Most Recent":
        filtered_df = filtered_df.sort_values('scraped_at', ascending=False)
    elif sort_by == "Company":
        filtered_df = filtered_df.sort_values('company')
    elif sort_by == "Location":
        filtered_df = filtered_df.sort_values('location')
    elif sort_by == "Source":
        filtered_df = filtered_df.sort_values('source')
    
    # Display results count
    st.header(f"📋 Results: {len(filtered_df)} job(s) found")
    
    if filtered_df.empty:
        st.info("No jobs match the selected filters. Try adjusting your filter criteria.")
    else:
        # Pagination
        items_per_page = 20  # Fixed number of items per page
        
        # Calculate pagination
        total_pages = (len(filtered_df) // items_per_page) + (1 if len(filtered_df) % items_per_page > 0 else 0)
        
        if 'page' not in st.session_state:
            st.session_state.page = 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("◀ Previous", disabled=(st.session_state.page == 1)):
                st.session_state.page -= 1
                st.rerun()
        
        with col2:
            st.write(f"Page {st.session_state.page} of {total_pages}")
        
        with col3:
            if st.button("Next ▶", disabled=(st.session_state.page >= total_pages)):
                st.session_state.page += 1
                st.rerun()
        
        # Calculate start and end indices
        start_idx = (st.session_state.page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        # Get current page data
        page_df = filtered_df.iloc[start_idx:end_idx]
        
        st.divider()
        
        # Display jobs
        for idx, job in page_df.iterrows():
            with st.container():
                # Create columns for job card
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader(job['title'])
                    st.write(f"**Company:** {job['company']}")
                    st.write(f"**Location:** {job['location']}")
                    st.write(f"**Source:** {job['source']}")
                    st.write(f"**Date Posted:** {job['date_posted']}")
                
                with col2:
                    st.write("")
                    if st.button("🔗 View Job", key=f"view_{idx}"):
                        st.markdown(f"[Open Job Listing]({job['url']})")
                
                st.divider()
        
        # Summary statistics
        st.sidebar.divider()
        st.sidebar.header("📊 Summary")
        st.sidebar.metric("Total Jobs", len(filtered_df))
        st.sidebar.metric("Unique Companies", filtered_df['company'].nunique())
        st.sidebar.metric("Unique Locations", filtered_df['location'].nunique())
        st.sidebar.metric("Data Sources", filtered_df['source'].nunique())
        
       