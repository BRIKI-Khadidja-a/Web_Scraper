import requests
from bs4 import BeautifulSoup
import lxml

title = []
company = []
location = []
date_posted = []

page_number = 0

# Requête HTTP avec headers pour éviter blocage
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

result = requests.get(f"https://wuzzuf.net/search/jobs?q=cyber%20security&start={page_number}", headers=headers)
src = result.content
soup = BeautifulSoup(src, "lxml")

titles = soup.find_all("h2", class_="css-193uk2c")
companies = soup.find_all("a", class_="css-ipsyv7")
locations = soup.find_all("span", class_="css-16x61xq")
posted_new = soup.find_all("div", {"class":"css-eg55jf"})
posted_old = soup.find_all("div", {"class":"css-1jldrig"})
posted = [*posted_new, *posted_old]

# Pour éviter erreur si certaines listes ont des longueurs différentes, on prend le minimum
length = min(len(titles), len(companies), len(locations), len(posted))

for i in range(length):
    title.append(titles[i].get_text(strip=True))
    company.append(companies[i].get_text(strip=True))
    location.append(locations[i].get_text(strip=True))
    date_posted.append(posted[i].get_text(strip=True))

# Affichage des résultats dans le terminal
for i in range(length):
    print(f"Job {i+1}:")
    print(f" Title      : {title[i]}")
    print(f" Company    : {company[i]}")
    print(f" Location   : {location[i]}")
    print(f" Date Posted: {date_posted[i]}")
    print("-" * 40)