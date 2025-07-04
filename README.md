# Alumni Tracer using Playwright based Linkedin Crawler 

## Overview
The LinkedIn Crawler is a Python-based automation tool that uses Playwright to extract LinkedIn profile data for a list of names provided in a CSV file. The extracted data includes basic profile information, education, experiences, and skills, which are saved into separate CSV files for easy analysis.

## Project Structure
```
linkedincrawler/
├── Main.py                # Main script to run the LinkedIn crawler
├── txt2csv.py             # Script to generate the input CSV file with names
├── data/
│   ├── AlumniLists/
│   │   └── InputNames.csv # Input file containing names to search
│   ├── ExtractedData/     # Directory where extracted data is saved
├── logs/                  # Directory for logging (optional)
```

## Features
- **Automated LinkedIn Login**: Logs into LinkedIn using user-provided credentials.
- **Profile Search**: Searches for profiles based on names provided in `InputNames.csv`.
- **Data Extraction**: Extracts profile information, education, experiences, and skills.
- **Incremental Data Saving**: Saves extracted data incrementally into separate CSV files:
  - `ExtractedProfiles.csv`: Contains basic profile information (name, headline, location).
  - `Education.csv`: Contains education details for each profile.
  - `Experiences.csv`: Contains work experience details for each profile.
  - `Skills.csv`: Contains skills listed on each profile.

## Requirements
- Python 3.10 or higher
- Playwright
- pandas
- fuzzywuzzy
- python-Levenshtein (optional for faster fuzzy matching)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/PjayFX/AlumniTracer_playwright.git
   cd AlumniTracer_playwright
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Usage

### Step 1: Generate Input CSV
Run the `txt2csv.py` script to generate the `InputNames.csv` file in the `data/AlumniLists` directory:
```bash
python txt2csv.py
```

### Step 2: Run the LinkedIn Crawler
Run the `Main.py` script to start the LinkedIn crawler:
```bash
python Main.py
```

You will be prompted to enter your LinkedIn username and password.

### Step 3: View Extracted Data
After the script finishes, the extracted data will be saved in the `data/ExtractedData` directory:
- `ExtractedProfiles.csv`
- `Education.csv`
- `Experiences.csv`
- `Skills.csv`

## Logging
Logs can be optionally saved in the `logs/` directory for debugging purposes.

## Notes
- Ensure your LinkedIn account has access to the profiles you want to scrape.
- Use responsibly and comply with LinkedIn's terms of service.

## License
This project is licensed under the MIT License.

## Author
Created by [PjayFX](https://github.com/PjayFX).