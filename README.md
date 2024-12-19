# Trello Scraper

A Python-based tool to scrape Trello boards and analyze card data. This tool allows you to:
- Login to Trello
- Get all cards for a specific member of a board
- Export card data to a readable format
- Generate resume-friendly bullet points using GPT (optional)

## Requirements

- Python 3.6+
- Chrome browser
- ChromeDriver (automatically managed by webdriver_manager)
- Trello account credentials
- OpenAI API key (optional, for resume generation)

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

4. Create a .env file with your credentials:

```
TRELLO_EMAIL=<your_trello_email>
TRELLO_PASSWORD=<your_trello_password>
TRELLO_USERNAME=<your_trello_username>
OPENAI_API_KEY=<your_openai_api_key>  # Optional, for resume generation
```

## Usage

### Basic Usage (Card List Only)
```bash
python trello_scraper.py --member <trello_username>
```

### Generate Resume Points
```bash
python trello_scraper.py --member <trello_username> --generate-resume
```

## Output Files

- `card_list.txt`: Detailed list of all cards with descriptions and checklists
- `resume_points.txt`: AI-generated resume bullet points (if --generate-resume is used)

## Notes

- The script can run in both headless and visible browser modes
- Resume generation requires an OpenAI API key and sufficient API quota
- All sensitive data should be stored in the .env file


