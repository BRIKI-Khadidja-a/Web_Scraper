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
input_element.send_keys("cybersecurity" + Keys.ENTER)

time.sleep(10)

# close the browser
driver.quit()
