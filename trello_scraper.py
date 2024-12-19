import os
from datetime import datetime
from xml.etree.ElementTree import Element
import pandas as pd
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
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
            time.sleep(0.5)
            
            # Click the Atlassian continue button
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "login-submit"))
            )
            continue_button.click()
            time.sleep(0.5)
            
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
            raise
        
    def navigate_to_sprint_room(self):
        """Navigate to the member's boards page."""
        try:
            self.driver.get(f"https://trello.com/b/AKnpNx3h/sprint-room")
            time.sleep(1)
            # look for <h1 class="HKTtBLwDyErB_o" data-testid="board-name-display">Sprint Room</h1>
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "HKTtBLwDyErB_o"))
            )
        except Exception as e:
            print(f"Failed to navigate to sprint room: {str(e)}")
            raise
        
    def get_sprint_room_user_cards(self, member):
        """Get all cards for the user in the sprint room."""
        try:
            # Wait for the page to be fully loaded
            time.sleep(3)  # Increased wait time for page stability
            
            # set up filter for cards assigned to user: https://trello.com/b/AKnpNx3h/sprint-room?filter=member:nicholasbyrne13
            self.driver.get(f"https://trello.com/b/AKnpNx3h/sprint-room?filter=member:{member}")
            time.sleep(3)
            
        except Exception as e:
            print(f"Failed to get sprint room user cards: {str(e)}")
            raise
        
    def export_view_json(self):
        """Export the view to a JSON file."""
        try:
            # see if menu button is open
            # menu_title = <h3 class="MK0fS4D9AGgvuD">Menu</h3>
            menu_title = self.driver.find_element(By.CLASS_NAME, "MK0fS4D9AGgvuD")
            if menu_title.is_displayed() == False:
                # open menu (the three dots)
                time.sleep(1)
                menu_button = self.driver.find_element(By.CLASS_NAME, "GDunJzzgFqQY_3")
                menu_button1 = self.wait.until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "GDunJzzgFqQY_3"))
                )
                try:
                    menu_button1.click()
                except:
                    menu_button.click()
                time.sleep(1.5)
                
            # click on export/print/share button
            export_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//div[contains(text(), 'Print, export, and share')]]"))
            )
            export_button.click()
            
            # Wait for the export dialog to fully appear
            time.sleep(2)
            
            # Wait for and click on export JSON using the link text
            export_as_json_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//a[.//span[contains(text(), 'Export as JSON')]]"))
            )
            # Wait a moment before clicking to ensure the element is truly interactive
            time.sleep(1)
            export_as_json_button.click()
            
            # Wait for download to begin
            time.sleep(2)
            
            # Wait for download to complete
            time.sleep(2)
            print("Downloading...")
            
            # move file from downloads folder to current directory
            # os.rename(os.path.join(os.path.expanduser('~'), 'Downloads', 'export.json'), 'export.json')
            
        except Exception as e:
            print(f"Failed to export view: {str(e)}")
            self.driver.save_screenshot("export_error.png")
            raise
        
    def verify_download(self):
        """Verify the download is complete."""
        try:
            # check if .json file exists in downloads folder
            if os.path.exists(os.path.join(os.path.expanduser('~'), 'Downloads', 'AKnpNx3h - Sprint Room.json')):
                print("Download complete")
            else:
                print("Download failed")
        except Exception as e:
            print(f"Failed to verify download: {str(e)}")
            raise

    def __del__(self):
        """Clean up browser instance."""
        self.driver.quit()

@click.command()
@click.option('--member', required=True, help='Trello username to scrape')
def main(member):
    scraper = TrelloScraper()
    
    try:
        scraper.get_sprint_room_user_cards(member)
        time.sleep(2)  # Wait for filtered view to stabilize
        scraper.export_view_json()
        scraper.verify_download()
    except Exception as e:
        print(f"Operation failed: {str(e)}")
        scraper.driver.save_screenshot("error.png")
        raise e
    finally:
        scraper.driver.quit()

if __name__ == '__main__':
    main() 