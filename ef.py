"""SELENIEUM pr ouvrir un vrai navigateur web,
taper des choses, cliquer, lire du texte, naviguer,
comme le ferait un humain."""
"""Chrome = voiture
Selenium = le conducteur
 ChromeDriver = le volant qui les relie"""
import time #pr la pause du temps
import csv
import re
from datetime import datetime, timedelta #pr manipuler les dates et faire des operations sur les dates 
from selenium import webdriver #le conducteur du navigateur ,le vrai navigateur contrôlé par ton code
from selenium.webdriver.common.by import By #pour indiquer comment tu veux chercher un elt
from selenium.webdriver.chrome.service import Service #chromedriver.exe,pour lancer le bon ChromeDriver
from selenium.webdriver.chrome.options import Options #configurer chrome avant de le lancer
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait #permet de patienter jusqua ce qu'une condition soit remplie
from selenium.webdriver.support import expected_conditions as EC #expected condition

#fonction pour nettoyer les textes qu'on récupère du site avant de les enregistrer
def normalize_text(s): 
    return s.strip() if s else "—"

#fonction s'occupe d'une seule carte d’offre d’emploi
def extract_from_card(card):
    """Extrait Titre / Entreprise / Lieu / Date / Lien depuis une carte d'offre"""
    try:
        title = normalize_text(card.find_element(By.CSS_SELECTOR, "h2.t4.media-heading").text)
    except:
        title = "—"

    try:
        a = card.find_element(By.CSS_SELECTOR, "a[href*='/offres/recherche/detail/']")
        url = a.get_attribute("href")
    except:
        url = "—"

    # --- Extraction + conversion de la date ---
    date_posted = "—"
    try:
        date_texte = normalize_text(card.find_element(By.CSS_SELECTOR, "p.date").text.lower())
        aujourd_hui = datetime.now().date()

        if "aujourd" in date_texte:  # aujourd'hui
            date_posted = aujourd_hui
        elif "hier" in date_texte:
            date_posted = aujourd_hui - timedelta(days=1)
        elif "il y a" in date_texte:
            match = re.search(r"il y a (\d+)", date_texte)
            if match:
                jours = int(match.group(1))
                date_posted = aujourd_hui - timedelta(days=jours)
        elif "le" in date_texte:
            mois_fr = {
                "janvier": 1, "février": 2, "mars": 3, "avril": 4, "mai": 5, "juin": 6,
                "juillet": 7, "août": 8, "septembre": 9, "octobre": 10,
                "novembre": 11, "décembre": 12
            }
            match = re.search(r"le (\d{1,2}) ([a-zéû]+) (\d{4})", date_texte)
            if match:
                jour = int(match.group(1))
                mois = mois_fr.get(match.group(2), 1)
                annee = int(match.group(3))
                date_posted = datetime(annee, mois, jour).date()
        else:
            date_posted = aujourd_hui  # fallback
    except:
        pass

    
    #On récupère le texte du paragraphe sous le titre
    company = "—"
    location = "—"
    try:
        p_sub = card.find_element(By.CSS_SELECTOR, "p.subtext")
        text = p_sub.text.strip()
        parts = text.split(" - ")
        if len(parts) >= 2:
            entreprise = parts[0].strip()
            location = " - ".join(parts[1:]).strip() #tous les elts apr le premier
        else:
            company = text
    except:
        pass

    return {
        "Title": title,
        "Company": company,
        "Location": location,
        "Date_Posted": str(date_posted),
        "Url": url
    }


def main():
    print("===  Récupération des offres en Cyber Sécurité... ===")

    chrome_driver_path = r"C:\Users\BAB AL SAFA\Desktop\WebScraping\chromedriver.exe" #pilote le vrai chrome

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1000")

    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    try:
        url = "https://candidat.francetravail.fr/offres/recherche?motsCles=cyber+securite&offresPartenaires=true&tri=0"
        driver.get(url)

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.result"))) #c’est la balise HTML utilisée sur le site pour représenter chaque offre d’emploi

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

            # --- Cliquer sur "Afficher les 20 offres suivantes" ---
            try:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") #il scrolle jusqu’en bas de la page
                time.sleep(2)

                bouton_suivant = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Afficher les 20 offres suivantes')]")) #on cherche un lien (<a>) dont le texte contient "Afficher les 20 offres suivantes"
                )

                driver.execute_script("arguments[0].scrollIntoView(true);", bouton_suivant)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", bouton_suivant)

                # Attendre l’apparition de nouvelles offres
                wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "li.result")) > len(cards))
                page += 1

            except TimeoutException:
                print(" Fin des offres (plus de lien visible).")
                break
            except NoSuchElementException:
                print("Lien introuvable (probablement dernière page).")
                break

        print(f"\nTotal d'offres collectées : {len(offres)}\n")

        # Sauvegarde CSV
        with open("offres_cyber.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["Title", "Company", "Location", "Date_Posted", "Url"])
            writer.writeheader()
            writer.writerows(offres)

        print(" Données enregistrées dans 'offres_cyber.csv'")

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
