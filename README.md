# Tibbiportal.az Async Doctor Scraper

High-performance async scraper for tibbiportal.az that collects doctor information and saves it to CSV. Uses asyncio and aiohttp for concurrent requests, making it significantly faster than traditional scrapers.

## Features

- **Async/concurrent scraping** - Much faster than synchronous scrapers
- Scrapes all 214 pages of doctor listings
- Extracts detailed information from each doctor's page
- Saves data to CSV format
- Progress saving after each batch
- Error handling and automatic retry logic
- Concurrent connection limiting (configurable)
- Real-time progress tracking with statistics

## Performance

The async implementation processes multiple doctors concurrently:
- Configurable batch size (default: 5 pages at a time)
- Configurable max concurrent connections (default: 10)
- Expected completion time: 15-30 minutes for all 2136+ doctors
- Real-time statistics showing doctors/second rate

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

Install required dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install aiohttp beautifulsoup4
```

## Usage

### Full Scrape (All 214 Pages)

To scrape all doctors:

```bash
python scrape_doctors.py
```

The scraper will:
- Process pages in batches (default: 5 pages per batch)
- Use concurrent connections (default: 10 max concurrent)
- Display real-time progress and statistics
- Save progress after each batch
- Complete in approximately 15-30 minutes

### Custom Configuration

You can modify the configuration in `scrape_doctors.py` at the top of the `main()` function:

```python
# Configuration
start_page = 1          # First page to scrape
end_page = 214          # Last page to scrape
batch_size = 5          # Process N listing pages at a time
max_concurrent = 10     # Max concurrent connections per batch
```

**Examples:**

Test with first 5 pages:
```python
start_page = 1
end_page = 5
```

More aggressive scraping (faster, but may overload server):
```python
batch_size = 10
max_concurrent = 20
```

Conservative scraping (slower, more polite):
```python
batch_size = 3
max_concurrent = 5
```

## Output Files

- `doctors_data_complete.csv` - Final output with all scraped data
- `doctors_data_progress_page_X.csv` - Progress snapshots after each batch
- `doctors_data_interrupted.csv` - Data saved if you interrupt with Ctrl+C
- `doctors_data_error.csv` - Data saved if an error occurs

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

The scraper includes robust error handling:

- Automatic retry on failed requests (up to 3 attempts)
- Progress saving after each batch
- Graceful handling of Ctrl+C interruption
- Saves progress even if errors occur
- Semaphore limiting to prevent connection overload

## Scraping Etiquette

The scraper is designed to be efficient yet polite:

- Semaphore-controlled concurrent connections (default: 10 max)
- 1 second delay between batches
- Proper User-Agent header
- Timeout settings to prevent hanging
- Batch processing to avoid overwhelming the server

You can make it more conservative by reducing `max_concurrent` and `batch_size`.

## Troubleshooting

**Connection errors:**
- Check your internet connection
- The website might be temporarily down
- Try reducing `max_concurrent` and `batch_size` values
- Increase the delay between batches

**Missing data:**
- Some doctors may not have all fields filled
- Empty fields will appear as blank in the CSV

**Interrupted scraping:**
- The scraper saves progress after each batch
- If interrupted, check for `doctors_data_progress_page_X.csv` files
- Restart from the last saved batch by adjusting `start_page`

**Too many concurrent connections:**
- If you see many timeout errors, reduce `max_concurrent`
- Reduce `batch_size` to process fewer pages at once

## Example Output

When running, you'll see output like:

```
Tibbiportal.az Async Doctor Scraper
============================================================
Configuration:
  Pages to scrape: 1 to 214
  Batch size: 5 pages
  Max concurrent connections: 10
  Expected total doctors: ~2136
============================================================

Processing batch: pages 1-5
Scraping listing page 1...
Found 10 doctors on page 1
...

✓ Progress saved: 50 doctors scraped
  Time elapsed: 12.3s | Rate: 4.1 doctors/sec
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scrape_doctors.py
```

The scraper will handle everything automatically and save the final results to `doctors_data_complete.csv`.

## License

This scraper is for educational purposes only. Please respect tibbiportal.az's terms of service and robots.txt file.
