# script to scrape job listings from Emploitic (Algeria’s most popular job website)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# initialize Chrome WebDriver 
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# open the website homepage
driver.get("https://emploitic.com/")

# create a WebDriverWait object that defines a maximum wait time for 10 seconds
wait = WebDriverWait(driver, 10)

# wait until the search input element appears on the page or it will stop after 10 seconds
input_element = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-testid="search"]'))
)

# type the search world cybersecurity and press Enter to search for related jobs
search_job ="cybersecurity"
input_element.send_keys(search_job + Keys.ENTER)

time.sleep(2)  # brief pause after Enter


# wait for job items to load and find all job listings 
job_items = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li[data-testid="jobs-item"]'))
)

for index, job in enumerate(job_items, start=1):
    try:
        # extract job title
        title = job.find_element(By.CSS_SELECTOR, 'h2.MuiTypography-root').text
        
        # extract company name
        company = job.find_element(By.CSS_SELECTOR, 'p[data-testid="jobs-item-company"]').text
        
        # extract job URL
        job_link = job.find_element(By.CSS_SELECTOR, 'a.MuiLink-root').get_attribute('href')
        
        # extract location 
        location = job.find_elements(By.CSS_SELECTOR, 'div.MuiStack-root.mui-1lwc51h')[0].text
        
        # extract posting date
        date_posted = job.find_elements(By.CSS_SELECTOR, 'div.MuiStack-root.mui-1lwc51h')[1].text
        

        print(f"\n--- Job {index} ---")
        print(f"Title: {title}")
        print(f"Company: {company}")
        print(f"Location: {location}")
        print(f"Date Posted: {date_posted}")
        print(f"URL: {job_link}")
        print("-" * 40)
   
       
    except Exception as e:
        print(f"Error extracting data from a job listing: {e}")


print(f"\nTotal jobs found: {len(job_items)}")



# close the browser
driver.quit()
