"""
SELENIUM pour ouvrir un vrai navigateur web,
taper des choses, cliquer, lire du texte, naviguer,
comme le ferait un humain.
"""

import time
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys, os

# --- Import de la base de données ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db import create_db, insert_job
from webdriver_manager.chrome import ChromeDriverManager


BASE = "https://candidat.francetravail.fr"


def normalize_text(s):
    """Nettoie le texte récupéré (supprime espaces inutiles)."""
    return s.strip().replace("\n", " ").replace("\r", " ") if s else "—"


def extract_from_card(card):
    """Extrait Titre / Entreprise / Lieu / Date / Lien depuis une carte d'offre France Travail."""

    # --- Titre ---
    try:
        title = normalize_text(card.find_element(By.CSS_SELECTOR, "span.media-heading-title").text)
    except:
        title = "—"

        # --- Entreprise + Lieu ---
    try:
        subtext = card.find_element(By.CSS_SELECTOR, "p.subtext")

        # cas où il y a une entreprise + span
        spans = subtext.find_elements(By.TAG_NAME, "span")
        if spans:
            # Récupère le texte du span (ex : "95 - Éragny" ou "31 - Toulouse")
            location_text = normalize_text(spans[-1].text)
            location = re.sub(r"^\d+\s*-*\s*", "", location_text).strip()

            # Essaie de récupérer le texte avant le span (l’entreprise)
            full_text = normalize_text(subtext.text)
            company_part = full_text.replace(spans[-1].text, "").strip(" -\u00a0")
            company = company_part if company_part else "—"
        else:
            # Cas extrême : aucun <span> (rare)
            full_text = normalize_text(subtext.text)
            company = full_text if full_text else "—"
            location = "—"

    except Exception as e:
        company, location = "—", "—"

    # --- Date ---
    date_posted = None
    try:
        date_texte = normalize_text(card.find_element(By.CSS_SELECTOR, "p.date").text.lower())
        aujourd_hui = datetime.now().date()

        if "aujourd" in date_texte:
            date_posted = aujourd_hui
        elif "hier" in date_texte:
            date_posted = aujourd_hui - timedelta(days=1)
        elif "il y a" in date_texte:
            match = re.search(r"il y a (\d+)", date_texte)
            if match:
                jours = int(match.group(1))
                date_posted = aujourd_hui - timedelta(days=jours)
        else:
            match = re.search(r"(\d{1,2}) ([a-zéû]+) (\d{4})", date_texte)
            if match:
                mois_fr = {
                    "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                    "juillet": 7, "août": 8, "septembre": 9, "octobre": 10,
                    "novembre": 11, "décembre": 12
                }
                jour = int(match.group(1))
                mois = mois_fr.get(match.group(2), 1)
                annee = int(match.group(3))
                date_posted = datetime(annee, mois, jour).date()
            else:
                date_posted = aujourd_hui
    except:
        date_posted = None

    # --- URL ---
    try:
        first_link = card.find_element(By.CSS_SELECTOR, "a.media.with-fav")
        href = first_link.get_attribute("href")
        url = urljoin(BASE, href) if href else "—"
    except Exception as e:
        url = "—"
        print("⚠️ Erreur URL:", e)

    # --- Affichage dans le terminal ---
    print("\n🟢 Nouvelle offre détectée :")
    print(f"   📌 Titre      : {title}")
    print(f"   🏢 Entreprise : {company}")
    print(f"   📍 Lieu       : {location}")
    print(f"   📅 Date       : {date_posted}")
    print(f"   🔗 Lien       : {url}")
    print("   -----------------------------------------------")

    # --- Résultat final ---
    return {
        "source": "France Travail",
        "title": title,
        "company": company,
        "location": location,
        "date_posted": date_posted,
        "url": url
    }


def main():
    print("===  Récupération des offres en Cyber Sécurité... ===")

    create_db()

    options = Options()
    # options.add_argument("--headless=new")  # Active le mode sans interface si besoin
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1000")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    try:
        url = "https://candidat.francetravail.fr/offres/recherche?motsCles=cyber+securite&offresPartenaires=true&tri=0"
        driver.get(url)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.result")))

        offres = []
        page = 1

        while True:
            print(f"\n===  Lecture des offres (page {page}) ===")
            time.sleep(2)

            cards = driver.find_elements(By.CSS_SELECTOR, "li.result")
            print(f"→ {len(cards)} offres visibles actuellement.")

            for card in cards[len(offres):]:
                offre = extract_from_card(card)
                offres.append(offre)
                insert_job(offre)  # Insertion en base

            # --- Bouton "Afficher les 20 offres suivantes" ---
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

                bouton_suivant = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Afficher les 20 offres suivantes')]"))
                )

                driver.execute_script("arguments[0].scrollIntoView(true);", bouton_suivant)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", bouton_suivant)

                wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "li.result")) > len(cards))
                page += 1

            except TimeoutException:
                print("✅ Fin des offres (plus de lien visible).")
                break
            except NoSuchElementException:
                print("✅ Lien introuvable (probablement dernière page).")
                break

        print(f"\n✅ Total d'offres collectées : {len(offres)}")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()