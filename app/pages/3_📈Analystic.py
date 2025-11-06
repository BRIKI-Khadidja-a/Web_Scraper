import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import os
from pathlib import Path
from datetime import datetime

# Configuration de la page
st.set_page_config(page_title="Analytics - CyberScraper", page_icon="📊", layout="wide")

# Chemin vers la base de données
# Remonter d'un niveau depuis pages/ vers la racine, puis aller dans database/
import os
if os.path.exists('database/jobs.db'):
    DB_PATH = Path('database/jobs.db')
else:
    # Si lancé depuis un sous-dossier
    DB_PATH = Path(__file__).resolve().parent.parent / 'database' / 'jobs.db'

# Chargement des données depuis SQLite
@st.cache_data(ttl=300)  # Cache pendant 5 minutes
def load_data():
    try:
        # Vérifier que le fichier existe
        if not DB_PATH.exists():
            st.error(f"❌ Base de données introuvable à : {DB_PATH}")
            st.info(f"📁 Répertoire courant : {Path.cwd()}")
            st.info("💡 Assurez-vous que le dossier 'database' et le fichier 'jobs.db' existent.")
            return pd.DataFrame()
        
        conn = sqlite3.connect(DB_PATH)
        query = "SELECT * FROM jobs"
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            st.warning("⚠️ Aucune donnée disponible dans la base de données.")
            return pd.DataFrame()
        
        # Convertir les dates
        df['scraped_at'] = pd.to_datetime(df['scraped_at'])
        df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')
        
        return df
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données : {e}")
        st.info(f"📁 Chemin de la DB : {DB_PATH}")
        return pd.DataFrame()

# Charger les données
df = load_data()

# Vérifier si des données existent
if df.empty:
    st.title("📊 Analytics & Insights")
    st.info("🔍 Aucune donnée à afficher. Veuillez d'abord scraper des jobs depuis la page Browse.")
    st.stop()

# Titre
st.title("📊 Analytics & Insights")

# Bouton de rafraîchissement
if st.button("🔄 Refresh Data", help="Actualiser les données"):
    st.cache_data.clear()
    st.rerun()

st.markdown("---")

# ===== Section 0: Key Statistics =====
st.header("📈 Key Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_jobs = len(df)
    st.metric("Total Jobs", f"{total_jobs:,}")

with col2:
    unique_companies = df['company'].nunique()
    st.metric("Unique Companies", f"{unique_companies:,}")

with col3:
    unique_locations = df['location'].nunique()
    st.metric("Unique Locations", f"{unique_locations:,}")

with col4:
    sources_count = df['source'].nunique()
    st.metric("Data Sources", f"{sources_count}")

st.markdown("---")

# ===== Section 1: Geographic Distribution =====
st.header("🌍 Geographic Distribution")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Top 15 Locations")
    
    # Compter les jobs par localisation
    location_counts = df['location'].value_counts().head(15)
    
    # Créer le graphique en barres
    fig_locations = px.bar(
        x=location_counts.values,
        y=location_counts.index,
        orientation='h',
        labels={'x': 'Number of Jobs', 'y': 'Location'},
        color_discrete_sequence=['#0066CC']
    )
    
    fig_locations.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Number of Jobs",
        yaxis_title="",
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig_locations, use_container_width=True)

with col2:
    st.subheader("Location Statistics")
    
    # Tableau des statistiques par location
    location_stats = df.groupby('location').agg({
        'id': 'count',
        'company': 'nunique'
    }).reset_index()
    location_stats.columns = ['Location', 'Total Jobs', 'Companies']
    location_stats = location_stats.sort_values('Total Jobs', ascending=False).head(10)
    
    st.dataframe(
        location_stats,
        hide_index=True,
        use_container_width=True,
        height=400
    )

st.markdown("---")

# ===== Section 2: Scraping Timeline =====
st.header("📅 Scraping Timeline")

col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Jobs Scraped Over Time")
    
    # Grouper par date de scraping
    df['scrape_date'] = df['scraped_at'].dt.date
    jobs_per_date = df.groupby('scrape_date').size().reset_index(name='count')
    jobs_per_date = jobs_per_date.sort_values('scrape_date')
    
    # Créer le graphique de ligne
    fig_timeline = px.line(
        jobs_per_date,
        x='scrape_date',
        y='count',
        labels={'scrape_date': 'Date', 'count': 'Jobs Scraped'},
        color_discrete_sequence=['#0066CC'],
        markers=True
    )
    
    fig_timeline.update_layout(
        height=400,
        xaxis_title="Date",
        yaxis_title="Jobs Scraped",
        showlegend=False,
        hovermode='x unified'
    )
    
    fig_timeline.update_traces(line=dict(width=3), marker=dict(size=8))
    
    st.plotly_chart(fig_timeline, use_container_width=True)

with col2:
    st.subheader("Timeline Stats")
    
    # Statistiques de la timeline
    total_days = (df['scraped_at'].max() - df['scraped_at'].min()).days + 1
    avg_per_day = len(df) / total_days if total_days > 0 else 0
    
    st.metric("Total Days", total_days)
    st.metric("Avg per Day", f"{avg_per_day:.1f}")
    st.metric("Most Recent", df['scraped_at'].max().strftime('%Y-%m-%d'))
    st.metric("First Scrape", df['scraped_at'].min().strftime('%Y-%m-%d'))

st.markdown("---")

# ===== Section 3: Source Comparison =====
st.header("🔄 Source Comparison")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Source Statistics")
    
    # Tableau de comparaison des sources
    source_stats = df.groupby('source').agg({
        'id': 'count',
        'company': 'nunique',
        'location': 'nunique'
    }).reset_index()
    
    source_stats.columns = ['Source', 'Total Jobs', 'Unique Companies', 'Unique Locations']
    source_stats = source_stats.sort_values('Total Jobs', ascending=False)
    
    st.dataframe(
        source_stats,
        hide_index=True,
        use_container_width=True
    )
    
    # Graphique en camembert des sources
    st.subheader("Distribution by Source")
    
    fig_pie = px.pie(
        source_stats,
        values='Total Jobs',
        names='Source',
        color_discrete_sequence=px.colors.sequential.Blues_r
    )
    
    fig_pie.update_layout(height=300, margin=dict(l=20, r=20, t=20, b=20))
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("Top Companies per Source")
    
    # Sélecteur de source
    sources = ['All'] + sorted(df['source'].unique().tolist())
    selected_source = st.selectbox(
        "Select Source",
        options=sources,
        key='source_selector'
    )
    
    # Filtrer par source
    if selected_source == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['source'] == selected_source]
    
    # Compter les entreprises
    company_counts = filtered_df['company'].value_counts().head(10)
    
    # Créer le graphique en barres horizontales
    fig_companies = px.bar(
        x=company_counts.values,
        y=company_counts.index,
        orientation='h',
        color_discrete_sequence=['#0066CC'],
        labels={'x': 'Number of Jobs', 'y': 'Company'}
    )
    
    fig_companies.update_layout(
        height=400,
        showlegend=False,
        xaxis_title="Number of Jobs",
        yaxis_title="",
        yaxis={'categoryorder': 'total ascending'},
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig_companies, use_container_width=True)

st.markdown("---")

# ===== Section 4: Top Companies Overall =====
st.header("🏢 Top Companies")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Companies with Most Job Postings")
    
    top_companies = df['company'].value_counts().head(15)
    
    fig_top_companies = px.bar(
        x=top_companies.values,
        y=top_companies.index,
        orientation='h',
        color=top_companies.values,
        color_continuous_scale='Blues',
        labels={'x': 'Number of Jobs', 'y': 'Company'}
    )
    
    fig_top_companies.update_layout(
        height=500,
        showlegend=False,
        xaxis_title="Number of Jobs",
        yaxis_title="",
        yaxis={'categoryorder': 'total ascending'},
        coloraxis_showscale=False
    )
    
    st.plotly_chart(fig_top_companies, use_container_width=True)

with col2:
    st.subheader("Recent Activity")
    
    # Jobs les plus récents
    recent_jobs = df.nlargest(10, 'scraped_at')[['company', 'title', 'source', 'scraped_at']]
    recent_jobs['scraped_at'] = recent_jobs['scraped_at'].dt.strftime('%Y-%m-%d %H:%M')
    recent_jobs.columns = ['Company', 'Title', 'Source', 'Scraped At']
    
    st.dataframe(
        recent_jobs,
        hide_index=True,
        use_container_width=True,
        height=400
    )

st.markdown("---")

# ===== Section 5: Data Quality Insights =====
st.header("🔍 Data Quality Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Completeness")
    
    completeness = {
        'Field': ['Title', 'Company', 'Location', 'Date Posted', 'URL'],
        'Complete': [
            df['title'].notna().sum(),
            df['company'].notna().sum(),
            df['location'].notna().sum(),
            df['date_posted'].notna().sum(),
            df['url'].notna().sum()
        ],
        'Total': [len(df)] * 5
    }
    
    completeness_df = pd.DataFrame(completeness)
    completeness_df['Percentage'] = (completeness_df['Complete'] / completeness_df['Total'] * 100).round(1)
    
    st.dataframe(completeness_df[['Field', 'Percentage']], hide_index=True, use_container_width=True)

with col2:
    st.subheader("Duplicates Check")
    
    total_urls = len(df)
    unique_urls = df['url'].nunique()
    duplicates = total_urls - unique_urls
    
    st.metric("Total Records", total_urls)
    st.metric("Unique URLs", unique_urls)
    st.metric("Duplicates", duplicates)

with col3:
    st.subheader("Database Info")
    
    db_size = DB_PATH.stat().st_size / 1024  # Size in KB
    
    st.metric("DB Size", f"{db_size:.2f} KB")
    st.metric("Tables", "1")
    st.metric("Last Update", df['scraped_at'].max().strftime('%Y-%m-%d %H:%M'))

# Footer
st.markdown("---")
st.markdown("**CyberScraper Analytics** - Real-time insights from Emploitic, France Travail & Wuzzuf")