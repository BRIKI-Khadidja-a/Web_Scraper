import streamlit as st

# sets page title and icon in the browser tab
st.set_page_config(page_title="About", page_icon="ℹ️")

st.title("ℹ️ About This App")
st.divider()# adds a horizontal line

st.header("App Background")
st.write(
    """
    **CyberScrape** was developed as an academic project to address the fragmented nature 
    of cybersecurity job searching. Instead of requiring job seekers to browse multiple 
    websites separately, this platform consolidates opportunities from various job boards 
    into a single, searchable dashboard.
    """
)
st.divider()
st.header("Technical Architecture")

st.subheader("1. Data Collection System")
st.write(
    """
    Automated web scrapers built with **Python** collect cybersecurity job postings from 
    three major job platforms in different countries.
    """
)

st.subheader("2. Analysis Dashboard")
st.write(
    """
    The **Streamlit-based dashboard** offers interactive access to all collected data, 
    allowing users to search, filter, visualize, and export cybersecurity job listings.
    """
)
st.divider()
st.header("Data Structure")
st.write(
    """
    The platform uses an **SQLite database** that stores structured information for each 
    job posting — including position title, company name, location, posting date, source 
    platform, and a direct link to the original listing.  
    This enables efficient filtering and meaningful data analysis.
    """
)

st.divider()
st.header("Use Cases")

col1, col2, col3 = st.columns(3)# split content into three columns

with col1:
    st.subheader("🎯 Job Seekers")
    st.write(
        """
        - Discover cybersecurity jobs from multiple sources.  
        - Filter by country, title, or company.  
        - Track hiring trends and emerging roles.
        """
    )

with col2:
    st.subheader("📊 Market Researchers")
    st.write(
        """
        - Analyze hiring patterns and specialization demand.  
        - Study geographic job distribution.  
        - Export data for advanced analysis.
        """
    )

with col3:
    st.subheader("🎓 Career Advisors")
    st.write(
        """
        - Identify in-demand skills and certifications.  
        - Guide students using real market data.  
        - Track the evolution of cybersecurity job offers.
        """
    )

st.divider()
st.header("Project Team")
st.write(
    """
    Developed collaboratively by a team of **three computer engineering students** 
    as part of an academic project for an **advanced programming course** .
    """
)
# Footer
st.divider()
st.caption("🛡️ CyberScrape • Academic Project • 2025–2026")
