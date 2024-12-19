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

1. Create and activate a virtual environment:

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

2. Clone the repository:

```bash
git clone https://github.com/yourusername/trello-scraper.git
cd trello-scraper
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a .env file with the following variables:

```
TRELLO_EMAIL=<your_trello_email>
TRELLO_PASSWORD=<your_trello_password>
```

5. Run the script:

```bash
python trello_scraper.py --member <trello_username>
```

Note: Remember to activate the virtual environment every time you work on the project:
```bash
# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```


