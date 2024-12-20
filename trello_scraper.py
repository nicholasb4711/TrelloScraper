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
from model import get_resume_points

class TrelloScraper:
    def __init__(self, board_name):
        load_dotenv()
        self.board_name = board_name
        self.board_id = None
        self.driver = self._setup_driver()
        self.wait = WebDriverWait(self.driver, 10)
        try:
            self.login()
            self.find_board_id()
        except Exception as e:
            self.driver.quit()
            raise e

    def _setup_driver(self):
        """Configure and return Chrome driver with optimized settings."""
        print("Setting up driver")
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-browser-side-navigation')
        # options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.page_load_strategy = 'eager'
        print("Driver setup complete")
        return webdriver.Chrome(options=options)

    def login(self):
        """Login to Trello with credentials from .env file."""
        try:
            print("Logging in")
            self.driver.get("https://trello.com/login")
            
            # Enter email
            email_input = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
            email_input.send_keys(os.getenv('TRELLO_EMAIL'))
            
            # Submit email
            self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit"))).click()
            time.sleep(2)
            
            # Enter password
            password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            password_input.send_keys(os.getenv('TRELLO_PASSWORD'))
            
            # Submit password
            self.wait.until(EC.element_to_be_clickable((By.ID, "login-submit"))).click()
            
            # Verify login success
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "all-boards")))
            print("Login successful")
        except Exception as e:
            print(f"Login failed: {str(e)}")
            raise

    def get_board_user_cards(self, member):
        """Get filtered view of user's cards."""
        print("Getting user's cards")
        url = f"https://trello.com/b/{self.board_id}?filter=member:{member}"
        self.driver.get(url)
        time.sleep(3)  # Wait for filter to apply
        print("User's cards fetched")

    def export_view_json(self):
        """Export board data as JSON."""
        try:
            print("Exporting JSON")
            self.driver.get(f"https://trello.com/b/{self.board_id}.json")
            json_content = self.driver.page_source
            board_filename = self.board_name.replace(" ", "-")
            filename = f"board-{board_filename}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(json_content)
            
            print("JSON exported successfully")
            
        except Exception as e:
            print(f"Export failed: {str(e)}")
            raise

    def analyze_json(self):
        """Process JSON data and extract card information."""
        try:
            print("Analyzing JSON")
            board_filename = self.board_name.replace(" ", "-")
            filename = f"board-{board_filename}.json"
            with open(filename, "r") as f:
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
            
            # Only save card list, resume generation is handled separately
            self._save_card_list(df)
            
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
        print("Processing cards")
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
        
        print("Cards processed")
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
        print("Saving card list")
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
        """Generate resume bullet points using OpenAI."""
        try:
            print("Generating resume points")
            if df is None or df.empty:
                print("No cards found to analyze")
                return

            # Prepare data for GPT
            cards_by_label = {}
            for _, card in df.iterrows():
                for label in card['labels']:
                    if label not in cards_by_label:
                        cards_by_label[label] = []
                    cards_by_label[label].append({
                        'name': card['name'],
                        'description': card['desc'],
                        'completed_tasks': [
                            item['name'] 
                            for checklist in card['checklists'] 
                            for item in checklist['items'] 
                            if item['complete']
                        ]
                    })

            # Create prompt
            prompt = """Based on the following work history from Trello cards, create professional resume bullet points. 
            Focus on impact, technical skills, and quantifiable achievements. Group by category and make it concise yet impressive.
            
            Here are the cards organized by category:\n\n"""
            
            for label, cards in cards_by_label.items():
                prompt += f"\n{label}:\n"
                for card in cards:
                    prompt += f"\nProject: {card['name']}"
                    if card['description']:
                        prompt += f"\nDescription: {card['description']}"
                    if card['completed_tasks']:
                        prompt += "\nCompleted Tasks:\n- " + "\n- ".join(card['completed_tasks'])
                    prompt += "\n"

            # Get response from OpenAI
            response = get_resume_points(prompt)

            # Save response
            with open('resume_points.txt', 'w') as f:
                f.write("=== Resume Points Generated by GPT ===\n\n")
                f.write(response)

            print("Resume points saved to resume_points.txt")
            
        except Exception as e:
            print(f"Failed to generate resume points: {str(e)}")
            raise

    def __del__(self):
        """Clean up resources."""
        self.driver.quit()

    def find_board_id(self):
        """Find board ID from board name."""
        try:
            print(f"Finding board: {self.board_name}")
            self.driver.get("https://trello.com/u/me/boards")
            time.sleep(2)
            
            # Find all board links
            boards = self.wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/b/']"))
            )
            
            # Find matching board
            for board in boards:
                if self.board_name.lower() in board.text.lower():
                    board_url = board.get_attribute('href')
                    self.board_id = board_url.split('/b/')[1].split('/')[0]
                    print(f"Found board ID: {self.board_id}")
                    return
                    
            raise Exception(f"Board '{self.board_name}' not found")
            
        except Exception as e:
            print(f"Failed to find board: {str(e)}")
            raise

@click.command()
@click.option('--member', required=True, help='Trello username to scrape')
@click.option('--board', required=True, help='Name of the Trello board')
@click.option('--generate-resume', is_flag=True, help='Generate resume points using GPT')
def main(member, board, generate_resume):
    scraper = TrelloScraper(board)
    try:
        scraper.get_board_user_cards(member)
        scraper.export_view_json()
        df = scraper.analyze_json()
        
        if generate_resume:
            try:
                scraper.generate_resume_points(df)
            except Exception as e:
                print(f"\nFailed to generate resume points: {str(e)}")
                print("Card list was still generated successfully.")
                
    except Exception as e:
        print(f"Operation failed: {str(e)}")
        raise e
    finally:
        scraper.driver.quit()

if __name__ == '__main__':
    main() 