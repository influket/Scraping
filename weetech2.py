import csv
import time
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

            # Try to find and click the "Older Posts" link if present
            try:
                # Locate the "Older Posts" button
                next_button = WebDriverWait(page_to_scrape, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'blog/page/')]"))
                )

                # Check if the URL is already on the last page
                current_url = page_to_scrape.current_url
                print(f"Current URL before clicking: {current_url}")

                # Scroll to the "Older Posts" button to make sure it's in view
                page_to_scrape.execute_script("arguments[0].scrollIntoView(true);", next_button)

                # Wait for the button to be clickable
                WebDriverWait(page_to_scrape, 10).until(EC.element_to_be_clickable(next_button))

                # Ensure that no other element is blocking the button (handle possible overlays)
                page_to_scrape.execute_script("arguments[0].click();", next_button)
                print("Found 'Older Posts' button, clicking it.")

                # Wait for the page to load after clicking (make sure the URL changes)
                WebDriverWait(page_to_scrape, 10).until(EC.url_changes(current_url))

                # Print the URL after clicking to check if it has changed
                new_url = page_to_scrape.current_url
                print(f"New URL after clicking: {new_url}")

                # Wait for the page to load fully before scraping again
                time.sleep(3)

                # Increment page count
                page_count += 1

            except (NoSuchElementException, TimeoutException, ElementClickInterceptedException) as e:
                print(f"No more pages to scrape or error encountered: {e}")
                break  # Break the loop if there's no "Older Posts" button or it's not clickable

        except TimeoutException:
            print("Timed out waiting for page elements to load.")
            break

# Close the browser after scraping is complete
page_to_scrape.quit()
