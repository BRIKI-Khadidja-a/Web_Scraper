# script to scrape job listings from Emploitic (Algeria’s most popular job website)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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


jobs_number =0
page = 1

while True:
    print(f"\n{'='*50}")
    print(f"Scraping Page {page}")
    print(f"{'='*50}")

    try:
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
                
               jobs_number+=1
               print(f"Job number : {jobs_number}")
               print(f"\nJob {index} on Page {page}")
               print(f"Title: {title}")
               print(f"Company: {company}")
               print(f"Location: {location}")
               print(f"Date Posted: {date_posted}")
               print(f"URL: {job_link}")
               print("-" * 40)

            except Exception as e:
                print(f"Error extracting data from job {index}: {e}")

        #check if the next page button is not disabled
        try:
            # find the next button
            next_button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Go to next page"]')
            
            # check if button has the disabled class
            button_classes = next_button.get_attribute('class')
            if 'Mui-disabled' in button_classes:
                print("\nReached the last page. Next button is disabled.")
                break
            
            #button is enabled so it scrolls to its view and click
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", next_button)
            time.sleep(1)
            
            # reference to current job item for staleness check
            first_job = job_items[0]
            
            #click the next button
            next_button.click()
            page += 1
            
            #wait for page content to refresh
            try:
                wait.until(EC.staleness_of(first_job))
                time.sleep(2)
            except TimeoutException:
                time.sleep(3)
                
        except NoSuchElementException:
            print("\nNo next button found.")
            break
        except Exception as e:
            print(f"\nError during pagination: {e}")
            break
            
    except Exception as e:
        print(f"\nError loading page {page}: {e}")
        break

# the final summary
print(f"\n{'='*50}")
print(f"Scraping Complete")
print(f"{'='*50}")
print(f"Total pages scraped: {page}")
print(f"Total jobs collected: {jobs_number}")


# close the browser
driver.quit()