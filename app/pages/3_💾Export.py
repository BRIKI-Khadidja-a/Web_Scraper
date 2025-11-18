import streamlit as st
import pandas as pd
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import io
import json

# Configuration de la page
st.set_page_config(page_title="Export - CyberScraper", page_icon="💾", layout="wide")

# Chemin vers la base de données
if os.path.exists('database/jobs.db'):
    DB_PATH = Path('database/jobs.db')
else:
    DB_PATH = Path(__file__).resolve().parent.parent / 'database' / 'jobs.db'

# Chargement des données depuis SQLite
@st.cache_data(ttl=300)
def load_data():
    try:
        if not DB_PATH.exists():
            st.error(f"❌ Base de données introuvable à : {DB_PATH}")
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
        return pd.DataFrame()

# Fonction pour convertir DataFrame en CSV
def convert_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Fonction pour convertir DataFrame en Excel
def convert_to_excel(df):
    """Convertit un DataFrame en fichier Excel avec gestion d'erreurs"""
    try:
        output = io.BytesIO()
        
        # Créer une copie pour éviter de modifier l'original
        df_export = df.copy()
        
        # Gérer les valeurs NaT/NaN dans les dates
        for col in df_export.select_dtypes(include=['datetime64']).columns:
            df_export[col] = df_export[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_export.to_excel(writer, index=False, sheet_name='Jobs')
            
            # Optionnel : Ajuster la largeur des colonnes
            worksheet = writer.sheets['Jobs']
            for column in worksheet.columns:
                max_length = 0
                column = [cell for cell in column]
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column[0].column_letter].width = adjusted_width
        
        return output.getvalue()
    
    except ImportError:
        st.error("❌ Le module 'openpyxl' n'est pas installé. Installez-le avec: pip install openpyxl")
        return None
    except Exception as e:
        st.error(f"❌ Erreur lors de la conversion Excel : {e}")
        return None

# Fonction pour convertir DataFrame en JSON
def convert_to_json(df):
    return df.to_json(orient='records', indent=2, date_format='iso').encode('utf-8')

# Titre
st.title("💾 Job Listings Dashboard")
st.markdown("---")

# Charger les données
df = load_data()

if df.empty:
    st.info("🔍 Aucune donnée à exporter. Veuillez d'abord scraper des jobs depuis la page Browse.")
    st.stop()

# Section Export Data
st.header("Export Data")

# Afficher le nombre total de records
total_records = len(df)
st.markdown(f"**Total records available:** {total_records}")

# Sélection du format d'export
st.subheader("Select export format")

export_format = st.radio(
    "",
    ["CSV", "Excel", "JSON"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# Section Export Filters
st.header("Export Filters")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sources to include")
    
    # Multiselect pour les sources
    all_sources = df['source'].unique().tolist()
    selected_sources = st.multiselect(
        "Select sources",
        options=all_sources,
        default=all_sources,
        label_visibility="collapsed"
    )

with col2:
    st.subheader("Date range (scraped)")
    
    # Date range picker
    min_date = df['scraped_at'].min().date()
    max_date = df['scraped_at'].max().date()
    
    date_range = st.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        label_visibility="collapsed"
    )

# Filtrer les données
filtered_df = df.copy()

# Filtre par source
if selected_sources:
    filtered_df = filtered_df[filtered_df['source'].isin(selected_sources)]

# Filtre par date
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[
        (filtered_df['scraped_at'].dt.date >= start_date) & 
        (filtered_df['scraped_at'].dt.date <= end_date)
    ]

# Mettre à jour le nombre de records filtrés
filtered_count = len(filtered_df)

st.markdown("---")

# Section Download
st.header("Download")

# Préparer les données pour l'export (sans la colonne id)
export_df = filtered_df.drop(columns=['id'], errors='ignore')

# Bouton de téléchargement selon le format
if export_format == "CSV":
    csv_data = convert_to_csv(export_df)
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name=f"jobs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
elif export_format == "Excel":
    excel_data = convert_to_excel(export_df)
    st.download_button(
        label="Download Excel",
        data=excel_data,
        file_name=f"jobs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
elif export_format == "JSON":
    json_data = convert_to_json(export_df)
    st.download_button(
        label="Download JSON",
        data=json_data,
        file_name=f"jobs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

st.info(f"📊 Ready to export: **{filtered_count}** jobs matching your criteria")

st.markdown("---")

# Section Preview
st.header("Preview")

# Afficher un aperçu des données (limité aux colonnes importantes)
preview_columns = ['title', 'company', 'location', 'date_posted', 'source']
available_columns = [col for col in preview_columns if col in export_df.columns]

# Afficher le dataframe avec formatage des dates
preview_df = export_df[available_columns].copy()

# Formater les dates pour l'affichage
if 'date_posted' in preview_df.columns:
    preview_df['date_posted'] = preview_df['date_posted'].dt.strftime('%Y-%m-%d')

# Afficher le tableau
st.dataframe(
    preview_df,
    use_container_width=True,
    height=400,
    hide_index=False
)

# Statistiques d'export
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Records to Export", filtered_count)

with col2:
    st.metric("Total Available", total_records)

with col3:
    percentage = (filtered_count / total_records * 100) if total_records > 0 else 0
    st.metric("Percentage", f"{percentage:.1f}%")

with col4:
    st.metric("Format", export_format)

# Footer
st.markdown("---")
st.markdown("**CyberScraper Export** - Download your job data in multiple formats")