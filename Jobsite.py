import requests
from bs4 import BeautifulSoup
import lxml

title = []
company = []
location = []
date_posted = []
links = []

page_number = 0

# Requête HTTP avec headers pour éviter blocage
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    result = requests.get(f"https://wuzzuf.net/search/jobs?q=cyber%20security&start={page_number}", headers=headers)
    src = result.content
    soup = BeautifulSoup(src, "lxml")
    
    titles = soup.find_all("h2", class_="css-193uk2c")
    companies = soup.find_all("a", class_="css-ipsyv7")
    locations = soup.find_all("span", class_="css-16x61xq")
    
    # Pour éviter erreur si certaines listes ont des longueurs différentes, on prend le minimum
    length = min(len(titles), len(companies), len(locations))
    
    for i in range(length):
        title.append(titles[i].get_text(strip=True))
        company.append(companies[i].get_text(strip=True))
        location.append(locations[i].get_text(strip=True))
        
        # Extraire la date à partir du parent du titre
        title_parent = titles[i].find_parent()
        date_elem = title_parent.find("div", class_=["css-eg55jf", "css-1jldrig"])
        if date_elem:
            date_text = date_elem.get_text(strip=True)
            date_posted.append(date_text)
        else:
            date_posted.append("N/A")
        
        # Extraire le lien du job
        job_link_elem = titles[i].find("a")
        if job_link_elem:
            job_link = job_link_elem.attrs.get('href', '#')
            if job_link.startswith('/'):
                job_link = "https://wuzzuf.net" + job_link
            links.append(job_link)
        else:
            links.append("#")
    
    # Affichage des résultats dans le terminal
    for i in range(length):
        print(f"Job {i+1}:")
        print(f" Title       : {title[i]}")
        print(f" Company     : {company[i]}")
        print(f" Location    : {location[i]}")
        print(f" Date Posted: {date_posted[i]}")
        print(f" Link        : {links[i]}")
        print("-" * 50)
    
    print(f"\n✓ Total jobs trouvés: {length}")
    
except requests.exceptions.RequestException as e:
    print(f"Erreur de requête: {e}")
except Exception as e:
    print(f"Erreur: {e}")
finally:
    print("Scraping terminé.")