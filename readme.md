# **E-Job Tracker**

**Compare and Monitor Job Offers Across Multiple Countries**

---

##  Project Idea

Our project aims to **scrape job offer data** (such as job title, company name, location, and job link) from **different job websites in three different countries**.  

Each team member is responsible for **one country**, using Python web scraping tools to extract job offers from a popular local job platform.  

All the collected data will be **combined and displayed in a desktop application**, allowing users to:
 
- **Compare job offers** across different countries.  
- **Track new job postings** and observe hiring trends internationally.  

---

##  How It Works

### 1. Scraping Phase  
- Each member writes a Python script that extracts job title, company name, location, and job link from a website in their assigned country.  
- The data is cleaned and saved in a consistent format (CSV file or database).  

### 2. Data Storage  
- All scripts store their data in a shared database.  
- Each update includes timestamps to track when each job was scraped.  

### 3. Analysis Phase  

- It can show **statistics and trends**, such as which countries have the most openings or which companies hire frequently.  

### 4. Desktop Application  
 
- Provides an interactive interface to **view, search, and filter job offers** .  
- Includes clickable links to open the job listing directly in a browser.  

---

## Expected Output

- A **functional desktop application** that lists and compares job offers from **three countries**.  
- Ability to **update job data regularly**.  
- A **local database or CSV file** storing all scraped job data.  
-  **statistics** showing international job trends.  


# **Installation & Setup Guide**

---

## Prerequisites

Before running the E-Job Tracker application, ensure you have the following installed on your system:

- **Python 3.8 or higher** 
- **pip** (Python package installer) - Usually comes with Python
- **Git** (optional) - For cloning the repository

---

## Installation Steps

### 1. Clone or Download the Project
```bash
# If using Git
git clone https://github.com/BRIKI-Khadidja-a/Web_Scraper.git
cd Web_Scraper

# Or download and extract the ZIP file from the repository
```
### 2. Create a Virtual Environment (Recommended)

Creating a virtual environment helps isolate project dependencies:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Required Dependencies

All necessary Python packages are listed in the `requirements.txt` file. Install them using:
```bash
pip install -r requirements.txt
```

---

## Running the Scrapers

Each country has its own scraper module.You can each scraper individually :

### Algeria (Emploitic)
```bash
python -m scrapers.emploitic
```
<<<<<<< HEAD
### France (France Travail)
```bash
python -m scrapers.FranceTravail
```
### Wuzzuf ( Egypt )
```bash
python -m scrapers.Jobsite
```

---

## Running the APP
```bash
streamlit run app/Dashboard.py
=======
## 📁 Project Structure
```
WEB_SCRAPER/
│
├── app/                                    # Desktop application
│   ├── pages/                              # Application pages/screens
│   │   ├── 1_Browse.py                    # Browse jobs page
│   │   ├── 2_Analytic.py                  # Analytics/statistics page
│   │   ├── 3_Export.py                    # Export data page
│   │   └── 4_About.py                     # About page
│   │
│   ├── utils/                              # Utility functions
│   │   └── Dashboard.py                    # Dashboard components
│   │
│   └── Dashboard.py                        # Main dashboard application
│
├── database/                               # Database files
│   ├── __pycache__/                       # Python cache files
│   ├── __init__.py                        # Database package initializer
│   ├── db.py                              # Database connection and operations
│   └── jobs.db                            # SQLite database file
│
├── scrapers/                               # Web scraping modules
│   ├── __pycache__/                       # Python cache files
│   ├── emploitic.py                       # Algeria job scraper (Emploitic)
│   ├── FranceTraval.py                    # France job scraper
│   └── Jobsite.py                         # Other country job scraper
│
├── tools/                                  # Additional tools and utilities
│
├── venv/                                   # Virtual environment
│
├── .gitignore                              # Git ignore file
├── pyvenv.cfg                              # Virtual environment configuration
├── readme.md                               # Project documentation
└── requirements.txt                        # Python dependencies
```
