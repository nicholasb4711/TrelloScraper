import os
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import click
import time

class TrelloScraper:
    def __init__(self):
        load_dotenv()
        
        # Configure Chrome options for faster startup
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-extensions')  # Disable extensions for faster loading
        chrome_options.add_argument('--disable-browser-side-navigation')  # Faster navigation
        chrome_options.add_argument('--dns-prefetch-disable')  # Disable DNS prefetching
        chrome_options.add_argument('--disable-infobars')  # Disable infobars
        chrome_options.add_argument('--disable-notifications')  # Disable notifications
        chrome_options.add_argument('--disable-popup-blocking')  # Disable popup blocking
        chrome_options.page_load_strategy = 'eager'  # Don't wait for all resources to load
        
        # Initialize the Chrome driver with options
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)  # Reduced wait time from 20 to 10 seconds
        
        try:
            self.login()
        except Exception as e:
            self.driver.quit()
            raise e

    def login(self):
        """Login to Trello."""
        try:
            self.driver.get("https://trello.com/login")
            time.sleep(1)  # Increased initial wait time
            
            # Login with Atlassian account
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(os.getenv('TRELLO_EMAIL'))
            time.sleep(1)
            
            # Click the Atlassian continue button
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login-submit"))
            )
            continue_button.click()
            time.sleep(1)
            
            # Wait for password field and submit
            password_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.send_keys(os.getenv('TRELLO_PASSWORD'))
            
            # Click the login button
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login-submit"))
            )
            login_button.click()
            
            time.sleep(2)
            
            # # check if 2-step selection is required
            # if self.driver.find_element(By.ID, "password-container"):
            #     # click on the 2-step selection button
            #     self.driver.find_element(By.ID, "password-container").click()
            #     time.sleep(1)
            
            # verify we're logged in
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "all-boards"))
            )
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            raise
        
    def navigate_to_sprint_room(self):
        """Navigate to the member's boards page."""
        self.driver.get(f"https://trello.com/b/AKnpNx3h/sprint-room")
        time.sleep(2)

    def __del__(self):
        """Clean up browser instance."""
        self.driver.quit()

@click.command()
@click.option('--member', required=True, help='Trello username to scrape')
def main(member):
    scraper = TrelloScraper()
    
    try:
        scraper.navigate_to_sprint_room()
        time.sleep(3)
    finally:
        scraper.driver.quit()

if __name__ == '__main__':
    main() 