import streamlit as st
from utils.db_utils import load_all_jobs,get_statistics
import plotly.express as px

# sets page title and icon in the browser tab
st.set_page_config(page_title="Dashboard", page_icon="📊")

# Title and introduction
st.title("🛡️ CyberScraper")
st.write("Aggregate, analyze, and discover cybersecurity opportunities across multiple job boards.")
st.divider()# adds a horizontal line

#platform overview
st.header("Platform Overview")
st.write(
"""
**CyberScraper** is an intelligent job market analysis tool designed to 
streamline the cybersecurity job search process.  
It automatically collects, aggregates, and analyzes job postings from multiple 
job boards, providing job seekers and researchers with insights into the global 
cybersecurity employment landscape.
"""
)

# Key features
st.divider()
st.header("What This Platform Offers")

# split content into two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Centralized Job Discovery")
    st.write(
    """
    Access cybersecurity positions from multiple job boards in one place — 
    no need to browse multiple websites.
    """
    )

    st.subheader("📊 Market Intelligence")
    st.write(
    """
    Discover hiring trends, top employers, and geographic distribution 
    across the cybersecurity job market.
    """
    )

with col2:
    st.subheader("🔍 Advanced Filtering")
    st.write(
    """
    Search and filter jobs by location, company, or keywords to find 
    the opportunities that fit your goals.
    """
    )

    st.subheader("💾 Data Export")
    st.write(
    """
    Export filtered job data for offline analysis, application tracking, 
    or resume targeting.
    """
    )

# Database statistics
st.divider()
st.header("Current Database Statistics")

# load statistics and job data
with st.spinner("Loading dashboard data..."):
    stats = get_statistics()
    df = load_all_jobs()

# show warning if no data available
if df.empty:
    st.warning("⚠️ No job data available. The database might be empty or there might be a connection issue.")
else:
    col1, col2, col3, col4 = st.columns(4)# display key metrics in four columns

    with col1:
        st.metric("Total Opportunities", stats['total_jobs'])
    with col2:
        st.metric("Hiring Companies", stats['companies'])
    with col3:
        st.metric("Job Locations", stats['locations'])
    with col4:
        st.metric("Data Sources", stats['sources'])

    # data sources

     #display each source with job count in a row of columns
    st.divider()
    st.header("Integrated Data Sources")
    sources = df['source'].unique()
    cols = st.columns(len(sources))
    for i, source in enumerate(sources):
        with cols[i]:
            count = len(df[df['source'] == source])
            st.info(f"**{source}**\n\n{count:,} jobs")

    #Pie chart: Job distribution by Source
    source_counts = df['source'].value_counts()
    fig = px.pie(values=source_counts.values, names=source_counts.index, 
                title="Distribution by Source",
                color_discrete_sequence=['#42A5F5', '#90CAF9', '#BBDEFB']
                )
    # render the pie chart in the app
    st.plotly_chart(fig)

# Call to Action
st.divider()
st.header("Get Started")
st.write(
"""
Use the sidebar to navigate between pages — explore job listings, 
analyze market trends, or export data for your research.  
"""
)
# create 4 buttons for navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Browse Jobs"):
        st.switch_page("./pages/1_📊Browse.py")
with col2:
    if st.button("🔍 Search Jobs"):
        st.switch_page("./pages/2_🔍Search.py")
with col3:
    if st.button("📈 Market Analytics"):
        st.switch_page("./pages/3_📈Analystic.py")
with col4:
    if st.button("💾 Export Jobs"):
        st.switch_page("./pages/4_💾Export.py")

# Footer
st.divider()
st.caption("🛡️ CyberScrape • 2025–2026")
