# Trello Scraper

A Python-based tool to scrape Trello boards and analyze card data. This tool allows you to:
- login to trello
- get all boards for a member
- get all cards for a specific member of a board
- get all checklists for a card
- get all comments for a card
- get all attachments for a card
- download the data to a csv file
- analyze the data and generate a resume-friendly activity summary

## Requirements

- Python 3.6+
- Chrome browser
- ChromeDriver (automatically managed by webdriver_manager)
- Trello account credentials

## Installation

1. Clone the repository:

2. Install the dependencies:

```bash
pip install -r requirements.txt
```

3. Create a .env file with the following variables:

```
TRELLO_EMAIL=<your_trello_email>
TRELLO_PASSWORD=<your_trello_password>
```

4. Run the script:

```bash
python trello_scraper.py --member <trello_username>
```


