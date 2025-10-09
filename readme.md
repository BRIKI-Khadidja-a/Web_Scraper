# **E-Price Tracker**

 **Compare and Monitor Product Prices Across Multiple Websites**

---

##  Project Idea

Our project aims to **scrape product data** (like name, price, and availability) from **three different e-commerce websites**.

Each team member will handle **one website** using Python web scraping tools .

Then, we will **combine all the scraped data** into a central database or file and display it in a **simple website** that allows users to:

- Compare prices for the same product across multiple stores.
- View when a product’s price has changed.
- See which store currently offers the lowest price.

---

##  How It Works

1. **Scraping Phase:**
    - Each member writes a Python script that extracts product name, price, and link from one website.
    - The data is cleaned and stored in a shared format (like a CSV file or a database).
2. **Data Storage:**
    - All scripts update the same database (e.g., SQLite or MongoDB).
    - Each time you re-run the scrapers (daily or weekly), new data is stored with timestamps.
3. **Analysis Phase:**
    - The backend compares old and new prices to detect changes.
    - It calculates which website currently has the lowest price for each product.
4. **Website (Frontend):**
    - Built with Flask or Streamlit .
    - Displays the products, current prices

##  Expected Output

- A functional website that compares product prices from 3 e-commerce sites.
- Ability to update data regularly.
- A report showing price evolution over time.