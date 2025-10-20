import requests
from bs4 import BeautifulSoup
import lxml

title = []
company = []
location = []
date_posted = []
links = []

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

        if not titles:  # Fin des pages
            break

        length = min(len(titles), len(companies), len(locations))
        for i in range(length):
            title.append(titles[i].get_text(strip=True))
            company.append(companies[i].get_text(strip=True))
            location.append(locations[i].get_text(strip=True))

            title_parent = titles[i].find_parent()
            date_elem = title_parent.find("div", class_=["css-eg55jf", "css-1jldrig"])
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date_posted.append(date_text)
            else:
                date_posted.append("N/A")

            job_link_elem = titles[i].find("a")
            if job_link_elem:
                job_link = job_link_elem.attrs.get('href', '#')
                if job_link.startswith('/'):
                    job_link = "https://wuzzuf.net" + job_link
                links.append(job_link)
            else:
                links.append("#")

        print(f"✓ Page {page_number + 1} scrapée ({length} offres)")

        # Passer à la page suivante
        page_number += 1

    # Affichage final
    for i in range(len(title)):
        print(f"Job {i+1}:")
        print(f" Title       : {title[i]}")
        print(f" Company     : {company[i]}")
        print(f" Location    : {location[i]}")
        print(f" Date Posted : {date_posted[i]}")
        print(f" Link        : {links[i]}")
        print("-" * 50)

    print(f"\n✓ Total jobs trouvés sur toutes les pages: {len(title)}")

except requests.exceptions.RequestException as e:
    print(f"Erreur de requête: {e}")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    print("Scraping terminé.")
