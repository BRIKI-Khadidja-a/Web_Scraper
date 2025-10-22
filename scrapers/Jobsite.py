import sqlite3
from database.db import insert_job
import requests
from bs4 import BeautifulSoup
import lxml

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

page_number = 0

try:
    while True:
        url = f"https://wuzzuf.net/search/jobs?q=cyber%20security&start={page_number}"
        result = requests.get(url, headers=headers)

        # Si la page est vide ou inexistante, on arrête la boucle
        if result.status_code != 200 or "Search results not found" in result.text:
            break

        soup = BeautifulSoup(result.content, "lxml")
        titles = soup.find_all("h2", class_="css-193uk2c")
        companies = soup.find_all("a", class_="css-ipsyv7")
        locations = soup.find_all("span", class_="css-16x61xq")

        if not titles:
            break

        length = min(len(titles), len(companies), len(locations))
        for i in range(length):
            # Récupération des données
            title_text = titles[i].get_text(strip=True)
            company_text = companies[i].get_text(strip=True)
            location_text = locations[i].get_text(strip=True)

            title_parent = titles[i].find_parent()
            date_elem = title_parent.find("div", class_=["css-eg55jf", "css-1jldrig"])
            date_text = date_elem.get_text(strip=True) if date_elem else "N/A"

            job_link_elem = titles[i].find("a")
            job_link = job_link_elem.attrs.get('href', '#') if job_link_elem else "#"
            if job_link.startswith('/'):
                job_link = "https://wuzzuf.net" + job_link

            # Insérer dans la base
            job_data = {
                'source': 'Wuzzuf',
                'title': title_text,
                'company': company_text,
                'location': location_text,
                'date_posted': date_text,
                'url': job_link
            }
            insert_job(job_data)

        print(f"✓ Page {page_number + 1} scrapée ({length} offres)")

        page_number += 1

    print("Scraping terminé, résultats enregistrés dans jobs.db")

except requests.exceptions.RequestException as e:
    print(f"Erreur de requête: {e}")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    print("Scraping terminé.")
