import os
import json
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
            # Get the JSON content
            self.driver.get("https://trello.com/b/AKnpNx3h.json")
            json_content = self.driver.page_source
            
            # Save to file in project directory
            filename = "sprint-room.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            print(f"JSON saved to {filename}")
            
        except Exception as e:
            print(f"Failed to export JSON: {str(e)}")
            raise
        
    def verify_download(self):
        """Verify the download is complete."""
        try:
            if os.path.exists("sprint-room.json"):
                print("JSON file saved successfully")
                return True
            print("JSON file not found")
            return False
        except Exception as e:
            print(f"Failed to verify file: {str(e)}")
            raise
        
    def analyze_json(self):
        """Analyze the JSON file."""
        try:
            with open("sprint-room.json", "r") as f:
                content = f.read()
                json_str = content.split('<pre>')[1].split('</pre>')[0] if '<pre>' in content else content
                data = json.loads(json_str)
                
                # Get member ID and create checklist lookup
                member_id = None
                checklists = {cl['id']: cl for cl in data.get('checklists', [])}
                
                for member in data.get('members', []):
                    if member.get('username') == os.getenv('TRELLO_USERNAME'):
                        member_id = member.get('id')
                        break
                
                if not member_id:
                    print("Member not found in board")
                    return
                
                # Extract cards with full details
                cards_data = []
                for card in data.get('cards', []):
                    if card.get('idMembers') and member_id in card.get('idMembers'):
                        # Get checklists for this card
                        card_checklists = []
                        for checklist_id in card.get('idChecklists', []):
                            if checklist_id in checklists:
                                checklist = checklists[checklist_id]
                                items = [
                                    {
                                        'name': item['name'],
                                        'complete': item['state'] == 'complete'
                                    }
                                    for item in checklist.get('checkItems', [])
                                ]
                                card_checklists.append({
                                    'name': checklist['name'],
                                    'items': items
                                })
                        
                        card_info = {
                            'name': card.get('name'),
                            'desc': card.get('desc'),
                            'due': card.get('due'),
                            'labels': [label.get('name') for label in card.get('labels', [])],
                            'url': card.get('url'),
                            'checklists': card_checklists
                        }
                        cards_data.append(card_info)
                
                df = pd.DataFrame(cards_data)
                print(f"\nFound {len(df)} cards assigned to you")
                self.list_cards(df)
                return df
                
        except Exception as e:
            print(f"Failed to analyze JSON: {str(e)}")
            raise

    def list_cards(self, df):
        """List all cards in a readable format and save to file."""
        try:
            if df is None or df.empty:
                print("No cards found")
                return
            
            with open('card_list.txt', 'w') as f:
                f.write("=== Your Cards ===\n")
                for idx, card in df.iterrows():
                    f.write(f"\n{idx + 1}. {card['name']}\n")
                    if card['due']:
                        f.write(f"   Due: {card['due']}\n")
                    if card['desc']:
                        f.write(f"   Description:\n{card['desc']}\n")  # Full description
                    if card['labels']:
                        f.write(f"   Labels: {', '.join(card['labels'])}\n")
                    if card['checklists']:
                        f.write("\n   Checklists:\n")
                        for checklist in card['checklists']:
                            f.write(f"   - {checklist['name']}:\n")
                            for item in checklist['items']:
                                status = "☒" if item['complete'] else "☐"
                                f.write(f"     {status} {item['name']}\n")
                    f.write(f"   URL: {card['url']}\n")
                    f.write("   " + "-"*50 + "\n")
            
            print(f"Card list saved to card_list.txt")
            
        except Exception as e:
            print(f"Failed to save card list: {str(e)}")
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
        scraper.analyze_json()
    except Exception as e:
        print(f"Operation failed: {str(e)}")
        raise e
    finally:
        scraper.driver.quit()

if __name__ == '__main__': 
    main() 