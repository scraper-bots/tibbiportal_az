# Tibbiportal.az Doctor Scraper

This project scrapes doctor information from tibbiportal.az and saves it to a CSV file.

## Features

- Scrapes all 214 pages of doctor listings
- Extracts detailed information from each doctor's page
- Saves data to CSV format
- Progress saving every 10 pages
- Error handling and retry logic
- Polite scraping with delays between requests

## Data Extracted

For each doctor, the scraper collects:

- Name
- Specialty/Specialties
- Years of experience
- Phone number
- Work hours
- Workplace name and URL
- Number of likes
- Profile URL

## Installation

1. Install required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install requests beautifulsoup4
```

## Usage

### Test Run (First Page Only)

To test the scraper with just the first page:

```bash
python test_scraper.py
```

This will create `doctors_data_test.csv` with data from the first page only.

### Full Scrape (All 214 Pages)

To scrape all doctors:

```bash
python scrape_doctors.py
```

**Note:** This will take several hours to complete as it:
- Scrapes 214 pages
- Visits each doctor's detail page (2136+ doctors)
- Includes polite delays between requests

### Custom Page Range

You can modify the page range in `scrape_doctors.py` by editing this line:

```python
scraper.scrape_all_doctors(start_page=1, end_page=214)
```

For example, to scrape only pages 1-50:

```python
scraper.scrape_all_doctors(start_page=1, end_page=50)
```

## Output Files

- `doctors_data_complete.csv` - Final output with all scraped data
- `doctors_data_progress_page_X.csv` - Progress snapshots (every 10 pages)
- `doctors_data_interrupted.csv` - Data saved if you interrupt with Ctrl+C
- `doctors_data_error.csv` - Data saved if an error occurs
- `doctors_data_test.csv` - Test output from test_scraper.py

## CSV Format

The output CSV includes these columns:

| Column | Description |
|--------|-------------|
| name | Doctor's full name |
| specialty | Primary specialty/specialties |
| specialty_preview | Specialty shown on listing page |
| experience | Years of experience |
| phone | Contact phone number |
| work_hours | Working hours |
| workplace | Name of medical facility |
| workplace_url | URL to workplace page |
| likes | Number of likes on profile |
| url | URL to doctor's profile |

## Error Handling

The scraper includes:

- Automatic retry on failed requests (up to 3 attempts)
- Progress saving every 10 pages
- Graceful handling of Ctrl+C interruption
- Saves progress even if errors occur

## Scraping Etiquette

The scraper is designed to be polite:

- 0.5 second delay between doctor detail pages
- 1 second delay between listing pages
- Proper User-Agent header
- Timeout settings to prevent hanging

## Troubleshooting

**Connection errors:**
- Check your internet connection
- The website might be temporarily down
- Try increasing the delay between requests

**Missing data:**
- Some doctors may not have all fields filled
- Empty fields will appear as blank in the CSV

**Interrupted scraping:**
- The scraper saves progress every 10 pages
- If interrupted, check for `doctors_data_progress_page_X.csv` files
- You can restart from the last saved page by adjusting `start_page`

## Example

```bash
# Install dependencies
pip install -r requirements.txt

# Test with first page
python test_scraper.py

# If test works, run full scrape
python scrape_doctors.py
```

## License

This scraper is for educational purposes only. Please respect tibbiportal.az's terms of service and robots.txt file.
