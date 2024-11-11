import csv
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException

# Set up WebDriver options (No headless mode)
options = Options()
options.add_argument('--disable-gpu')  # Disable GPU acceleration (useful for headless mode)
options.add_argument('--window-size=1920x1080')  # Set consistent window size

# Path to the ChromeDriver (ensure this path points to chromedriver.exe)
browser_driver = Service(r'E:\Chrome\chromedriver-win64\chromedriver.exe')  # Update with the correct path

# Initialize WebDriver with options
page_to_scrape = webdriver.Chrome(service=browser_driver, options=options)

# Navigate to the target page
page_to_scrape.get("https://www.weetechsolution.com/blog")

# Wait for the page to load
time.sleep(2)

# Open CSV file for writing with UTF-8 encoding (to handle special characters)
with open("scraped_blogs.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["TITLES", "TEXTS"])

    page_count = 1  # Start from page 1 (first page doesn't have a page number)

    while True:
        print(f"Scraping page {page_count}...")

        try:
            # Wait for the articles to load on the current page
            titles = WebDriverWait(page_to_scrape, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//a[@rel="bookmark"]'))
            )
            texts = page_to_scrape.find_elements(By.TAG_NAME, "p")  # Scraping all <p> tags

            # Write each title and text to CSV and print to the console
            for title, text in zip(titles, texts):
                print(f"{title.text} - {text.text}")
                writer.writerow([title.text, text.text])

            # Check for the "Older Posts" link and the "Previous" link
            try:
                # Check if the "Older Posts" link exists, which indicates there is a next page
                next_button = WebDriverWait(page_to_scrape, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'blog/page/')]"))
                )

                # Scroll to the "Older Posts" button to make sure it's in view
                page_to_scrape.execute_script("arguments[0].scrollIntoView(true);", next_button)

                # Retry clicking if the first attempt fails (e.g., element might be covered)
                try:
                    page_to_scrape.execute_script("arguments[0].click();", next_button)
                    print("Found 'Older Posts' button, clicking it.")

                    # Wait for the page to load after clicking
                    WebDriverWait(page_to_scrape, 10).until(EC.url_changes(page_to_scrape.current_url))
                    time.sleep(2)  # Allow for some time after page load

                    # Increment page count
                    page_count += 1
                except ElementClickInterceptedException:
                    print("Element not clickable. Trying again after a delay.")
                    time.sleep(2)  # Wait a little before trying again
                    next_button = page_to_scrape.find_element(By.XPATH, "//a[contains(@href, 'blog/page/')]")
                    page_to_scrape.execute_script("arguments[0].click();", next_button)
                    WebDriverWait(page_to_scrape, 10).until(EC.url_changes(page_to_scrape.current_url))
                    time.sleep(2)

            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
                print(f"Error encountered: {e}. No more pages to scrape.")
                break  # Break the loop if there's no "Older Posts" button or it's not clickable

        except TimeoutException:
            print("Timed out waiting for page elements to load.")
            break

# Close the browser after scraping is complete
page_to_scrape.quit()
