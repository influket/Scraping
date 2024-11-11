import csv
import time
import getpass
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

# Set up WebDriver options (optional headless mode)
options = Options()
# Optional: Run in headless mode (no browser window)
options.add_argument('--headless')  
# Disable GPU acceleration (useful for headless mode)
options.add_argument('--disable-gpu')  
# Set consistent window size
options.add_argument('--window-size=1920x1080')  

# Path to the ChromeDriver (ensure this path points to chromedriver.exe)
browser_driver = Service(r'E:\Chrome\chromedriver-win64\chromedriver.exe')  # Update with the correct path

# Initialize WebDriver with options
page_to_scrape = webdriver.Chrome(service=browser_driver, options=options)

# Navigate to the login page
page_to_scrape.get("http://quotes.toscrape.com")
page_to_scrape.find_element(By.LINK_TEXT, "Login").click()

# Wait for the login page to load
time.sleep(3)

# Login process
username = page_to_scrape.find_element(By.ID, "username")
password = page_to_scrape.find_element(By.ID, "password")
username.send_keys("admin")

# Get the password securely using getpass
my_pass = getpass.getpass(prompt="Enter your password: ")
password.send_keys(my_pass)

# Submit the login form
page_to_scrape.find_element(By.CSS_SELECTOR, "input.btn-primary").click()

# Open CSV file for writing with UTF-8 encoding
with open("scraped_quotes.csv", "w", newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["QUOTES", "AUTHORS"])

    # Start scraping quotes
    while True:
        # Get quotes and authors on the current page
        quotes = page_to_scrape.find_elements(By.CLASS_NAME, "text")
        authors = page_to_scrape.find_elements(By.CLASS_NAME, "author")

        # Write each quote and author to CSV and print to the console
        for quote, author in zip(quotes, authors):
            print(f"{quote.text} - {author.text}")
            writer.writerow([quote.text, author.text])

        try:
            # Try to click the "Next" button to go to the next page
            next_button = page_to_scrape.find_element(By.PARTIAL_LINK_TEXT, "Next")
            next_button.click()
            time.sleep(2)  # Sleep to wait for the page to load
        except NoSuchElementException:
            # Break the loop if there's no "Next" button (end of pages)
            print("No more pages to scrape.")
            break

# Close the browser after scraping is complete
page_to_scrape.quit()
