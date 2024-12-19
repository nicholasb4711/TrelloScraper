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
        self.driver = webdriver.Chrome()  # Make sure you have ChromeDriver installed
        self.wait = WebDriverWait(self.driver, 10)
        self.login()

    def login(self):
        """Login to Trello."""
        self.driver.get("https://trello.com/login")
        
        # Login with Atlassian account
        email_input = self.wait.until(EC.presence_of_element_located((By.ID, "user")))
        email_input.send_keys(os.getenv('TRELLO_EMAIL'))
        
        login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login")))
        login_button.click()
        
        # Wait for password field and submit
        password_input = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        password_input.send_keys(os.getenv('TRELLO_PASSWORD'))
        password_input.submit()
        
        # Wait for login to complete
        time.sleep(5)

    def get_member_boards(self, member_id):
        """Get all boards for a member."""
        self.driver.get(f"https://trello.com/{member_id}/boards")
        boards = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".board-tile")))
        return [board.get_attribute('href') for board in boards]

    def get_card_details(self, card_element):
        """Extract relevant details from a card."""
        try:
            # Click to open card
            card_element.click()
            time.sleep(1)
            
            title = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card-detail-title"))).text
            description = self.driver.find_element(By.CSS_SELECTOR, ".description-content").text
            labels = [label.text for label in self.driver.find_elements(By.CSS_SELECTOR, ".card-label")]
            
            # Close card
            self.driver.find_element(By.CSS_SELECTOR, ".dialog-close-button").click()
            time.sleep(0.5)
            
            return {
                'title': title,
                'description': description,
                'labels': labels,
                'board_name': self.driver.title
            }
        except Exception as e:
            print(f"Error processing card: {e}")
            return None

    def scrape_member_cards(self, member_id):
        """Scrape all cards for a member."""
        boards = self.get_member_boards(member_id)
        all_cards = []

        for board_url in boards:
            self.driver.get(board_url)
            time.sleep(2)
            
            cards = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".list-card")))
            for card in cards:
                card_details = self.get_card_details(card)
                if card_details:
                    all_cards.append(card_details)

        return all_cards

    def save_to_csv(self, cards, filename):
        """Save card details to CSV."""
        df = pd.DataFrame(cards)
        df.to_csv(filename, index=False)
        return filename

    def generate_summary(self, cards):
        """Generate a resume-friendly summary of activities."""
        df = pd.DataFrame(cards)
        
        summary = {
            'total_cards': len(df),
            'boards_contributed': df['board_name'].nunique(),
            'labels_summary': df['labels'].explode().value_counts().to_dict(),
        }
        
        return summary

    def __del__(self):
        """Clean up browser instance."""
        self.driver.quit()

@click.command()
@click.option('--member', required=True, help='Trello username to scrape')
def main(member):
    scraper = TrelloScraper()
    
    try:
        # Scrape cards
        print(f"Scraping cards for member: {member}")
        cards = scraper.scrape_member_cards(member)
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"trello_cards_{member}_{timestamp}.csv"
        scraper.save_to_csv(cards, filename)
        print(f"Cards saved to: {filename}")
        
        # Generate summary
        summary = scraper.generate_summary(cards)
        print("\nActivity Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")
    finally:
        scraper.driver.quit()

if __name__ == '__main__':
    main() 