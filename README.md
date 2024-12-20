# Trello Scraper

A Python automation tool that extracts and analyzes your Trello cards to generate professional documentation. This tool is particularly useful for:
- Documenting your work history from Trello boards
- Generating detailed reports of completed tasks
- Creating resume-friendly bullet points using AI
- Tracking project progress and achievements

## Features

- **Automated Login**: Securely connects to your Trello account
- **Board Selection**: Finds and accesses boards by name
- **Card Extraction**: Pulls all cards assigned to you, including:
  - Card descriptions
  - Completed checklist items
  - Labels and categories
  - Due dates
  - URLs for reference
- **Smart Formatting**: Organizes cards into a readable format
- **AI Resume Generation**: Optional GPT-powered feature that converts your Trello cards into professional resume bullet points

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
python trello_scraper.py --member <trello_username> --board "My Board Name"
```

### Generate Resume Points
```bash
python trello_scraper.py --member <trello_username> --board "My Board Name" --generate-resume
```

Note: The board name should match (or be contained in) the name of your Trello board. The search is case-insensitive.

## Output Files

- `card_list.txt`: Detailed list of all cards with descriptions and checklists
- `resume_points.txt`: AI-generated resume bullet points (if --generate-resume is used)
- `board-{name}.json`: Raw JSON data from the Trello board

## Notes

- The script supports both headless and visible browser modes (configurable in code)
- Resume generation requires an OpenAI API key and sufficient API quota
- All sensitive data should be stored in the .env file
- The tool respects Trello's rate limits and uses efficient data extraction methods

## Best Practices

1. Keep your .env file secure and never commit it to version control
2. Use descriptive board names for easier access
3. Ensure your Trello cards have good descriptions and completed checklists for better resume generation
4. Review and customize the generated resume points for accuracy

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](LICENSE)


