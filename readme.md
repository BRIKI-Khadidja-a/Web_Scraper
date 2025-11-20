# E‑Job Tracker

Modern Streamlit dashboard and scraper suite that centralizes internship/job offers, lets students apply directly, and enables companies to review applications stored in Supabase.

---

## ✨ Features
- Multi-country scrapers (Emploitic, France Travail, Wuzzuf) with unified schema.
- Streamlit dashboard with analytics, exports, and about pages.
- Student portal to browse internships, upload resumes, and apply with cover letters.
- Company portal to post internships, manage listings, and review/download resumes.
- Supabase backend for authentication, user roles, profiles, internships, and applications.

---

## 🧱 Tech Stack
- **Python / Streamlit** – UI + dashboards.
- **Supabase** – Auth + Postgres storage for users, profiles, internships, applications.
- **BeautifulSoup / requests** – Scrapers per region.
- **Pandas** – Data normalization & export.

---

## 🚀 Getting Started

### 1. Clone & Enter the Project
```bash
git clone https://github.com/BRIKI-Khadidja-a/Web_Scraper.git
cd Web_Scraper
```

### 2. Create & Activate a Virtual Environment
```bash
python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file (or export variables) with your Supabase credentials:
```bash
SUPABASE_URL=<your_supabase_project_url>
SUPABASE_KEY=<your_supabase_service_role_or_anon_key>
```

---

## 🛠 Running Components

### Scrapers
```bash
# Algeria (Emploitic)
python -m scrapers.emploitic

# France (France Travail)
python -m scrapers.FranceTravail

# Egypt (Wuzzuf)
python -m scrapers.Jobsite
```

### Streamlit App
```bash
streamlit run app/Dashboard.py
```
The Streamlit sidebar provides navigation between browse, analytics, export, about, and the new internship portal.

---

## 📂 Project Structure
```
WEB_SCRAPER/
├── app/
│   ├── Dashboard.py             # Streamlit entry point
│   ├── pages/
│   │   ├── 1_📊Browse.py
│   │   ├── 2_📈Analystic.py
│   │   ├── 3_💾Export.py
│   │   ├── 4_ℹ️About.py
│   │   └── 5_💼Internships.py   # Student + company portal
│   └── utils/
│       └── db_utils.py
├── database/
│   └── db.py
├── scrapers/
│   ├── emploitic.py
│   ├── FranceTravail.py
│   └── Jobsite.py
├── requirements.txt
└── readme.md
```

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-update`.
3. Commit & push your changes.
4. Open a pull request with context (screenshots encouraged).

---

## 📬 Support
Having trouble with setup or Supabase configuration? Open an issue or ping the maintainers with logs/screenshots so we can help quickly.

Enjoy tracking jobs and managing internships! 🎯
