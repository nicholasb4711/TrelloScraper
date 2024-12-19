import os
import json
import time
import click
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv

class TrelloScraper:
    def __init__(self):
        load_dotenv()
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        try:
            self.login()
        except Exception as e:
            self.driver.quit()
            raise e

    def _setup_driver(self):
        """Configure and return Chrome driver with optimized settings."""
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-browser-side-navigation')
        options.page_load_strategy = 'eager'
        return webdriver.Chrome(options=options)

    def login(self):
        """Login to Trello with credentials from .env file."""
        try:
            self.driver.get("https://trello.com/login")
            
            # Enter email
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_input.send_keys(os.getenv('TRELLO_EMAIL'))
            
            # Submit email
            self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit"))).click()
            time.sleep(1)
            
            # Enter password
            password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_input.send_keys(os.getenv('TRELLO_PASSWORD'))
            
            # Submit password
            self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit"))).click()
            
            # Verify login success
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "all-boards")))
            
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

    def get_sprint_room_user_cards(self, member):
        """Get filtered view of user's cards."""
        url = f"https://trello.com/b/AKnpNx3h/sprint-room?filter=member:{member}"
        self.driver.get(url)
        time.sleep(3)  # Wait for filter to apply

    def export_view_json(self):
        """Export board data as JSON."""
        try:
            self.driver.get("https://trello.com/b/AKnpNx3h.json")
            json_content = self.driver.page_source
            
            with open("sprint-room.json", 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            print("JSON exported successfully")
            
        except Exception as e:
            print(f"Export failed: {str(e)}")
            raise

    def analyze_json(self):
        """Process JSON data and extract card information."""
        try:
            # Read and parse JSON
            with open("sprint-room.json", "r") as f:
                content = f.read()
                json_str = content.split('<pre>')[1].split('</pre>')[0] if '<pre>' in content else content
                data = json.loads(json_str)
            
            # Get user's member ID
            member_id = self._get_member_id(data)
            if not member_id:
                return None
            
            # Process cards
            cards_data = self._process_cards(data, member_id)
            df = pd.DataFrame(cards_data)
            
            print(f"\nFound {len(df)} cards assigned to you")
            
            # Generate both card list and resume points
            self._save_card_list(df)
            self.generate_resume_points(df)
            
            return df
            
        except Exception as e:
            print(f"Analysis failed: {str(e)}")
            raise

    def _get_member_id(self, data):
        """Get member ID from username."""
        for member in data.get('members', []):
            if member.get('username') == os.getenv('TRELLO_USERNAME'):
                return member.get('id')
        print("Member not found in board")
        return None

    def _process_cards(self, data, member_id):
        """Extract card data including checklists."""
        checklists = {cl['id']: cl for cl in data.get('checklists', [])}
        cards_data = []
        
        for card in data.get('cards', []):
            if card.get('idMembers') and member_id in card.get('idMembers'):
                card_info = {
                    'name': card.get('name'),
                    'desc': card.get('desc'),
                    'due': card.get('due'),
                    'labels': [label.get('name') for label in card.get('labels', [])],
                    'url': card.get('url'),
                    'checklists': self._get_card_checklists(card, checklists)
                }
                cards_data.append(card_info)
        
        return cards_data

    def _get_card_checklists(self, card, checklists):
        """Process checklists for a card."""
        card_checklists = []
        for checklist_id in card.get('idChecklists', []):
            if checklist_id in checklists:
                checklist = checklists[checklist_id]
                items = [
                    {'name': item['name'], 'complete': item['state'] == 'complete'}
                    for item in checklist.get('checkItems', [])
                ]
                card_checklists.append({'name': checklist['name'], 'items': items})
        return card_checklists

    def _save_card_list(self, df):
        """Save formatted card list to file."""
        if df is None or df.empty:
            print("No cards found")
            return

        with open('card_list.txt', 'w') as f:
            f.write("=== Your Cards ===\n")
            for idx, card in df.iterrows():
                self._write_card_details(f, idx + 1, card)

        print("Card list saved to card_list.txt")

    def _write_card_details(self, file, index, card):
        """Write formatted card details to file."""
        file.write(f"\n{index}. {card['name']}\n")
        if card['due']:
            file.write(f"   Due: {card['due']}\n")
        if card['desc']:
            file.write(f"   Description:\n{card['desc']}\n")
        if card['labels']:
            file.write(f"   Labels: {', '.join(card['labels'])}\n")
        if card['checklists']:
            self._write_checklists(file, card['checklists'])
        file.write(f"   URL: {card['url']}\n")
        file.write("   " + "-"*50 + "\n")

    def _write_checklists(self, file, checklists):
        """Write formatted checklist details to file."""
        file.write("\n   Checklists:\n")
        for checklist in checklists:
            file.write(f"   - {checklist['name']}:\n")
            for item in checklist['items']:
                status = "☒" if item['complete'] else "☐"
                file.write(f"     {status} {item['name']}\n")

    def generate_resume_points(self, df):
        """Generate resume bullet points from card data."""
        try:
            if df is None or df.empty:
                print("No cards found to analyze")
                return

            # Group cards by label for better organization
            label_groups = {}
            for _, card in df.iterrows():
                for label in card['labels']:
                    if label not in label_groups:
                        label_groups[label] = []
                    label_groups[label].append({
                        'name': card['name'],
                        'desc': card['desc'],
                        'checklists': card['checklists']
                    })

            # Write resume points to file
            with open('resume_points.txt', 'w') as f:
                f.write("=== Resume Points by Category ===\n\n")
                
                for label, cards in label_groups.items():
                    f.write(f"\n{label.upper()}\n")
                    f.write("-" * 50 + "\n")
                    
                    # Combine similar cards and generate summary points
                    summary = (
                        f"• Led development of {len(cards)} projects including:\n"
                        + "\n".join(f"  - {card['name']}" for card in cards)
                        + "\n\n"
                        + "Key Achievements:\n"
                        + self._generate_achievements(cards)
                    )
                    f.write(summary + "\n")

            print("Resume points saved to resume_points.txt")
            
        except Exception as e:
            print(f"Failed to generate resume points: {str(e)}")
            raise

    def _generate_achievements(self, cards):
        """Generate achievement bullet points from cards."""
        achievements = []
        
        for card in cards:
            # Extract completed checklist items as accomplishments
            for checklist in card.get('checklists', []):
                completed_items = [
                    item['name'] for item in checklist['items'] 
                    if item['complete']
                ]
                if completed_items:
                    achievements.extend(completed_items)
            
            # Include card description if it provides value
            if card['desc'] and len(card['desc']) > 10:  # Arbitrary minimum length
                achievements.append(card['desc'].split('\n')[0])  # First line only
        
        # Format achievements as bullet points
        return "\n".join(f"• {achievement}" for achievement in achievements)

    def __del__(self):
        """Clean up resources."""
        self.driver.quit()

@click.command()
@click.option('--member', required=True, help='Trello username to scrape')
def main(member):
    scraper = TrelloScraper()
    try:
        scraper.get_sprint_room_user_cards(member)
        scraper.export_view_json()
        scraper.analyze_json()
    except Exception as e:
        print(f"Operation failed: {str(e)}")
        raise e
    finally:
        scraper.driver.quit()

if __name__ == '__main__':
    main() 