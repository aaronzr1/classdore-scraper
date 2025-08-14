# Course Scraper

This scraper is designed to extract course information from Vanderbilt University's course catalog.

## Structure

The scraper is organized into three main modules:

1. `keywords.py` - Handles the keyword-based scraping to find course listings
2. `listings.py` - Handles the detailed scraping of individual course information
3. `main.py` - Entry point for the scraper with command-line arguments

## Usage

```bash
# Run both keyword and listing scraping
python3 scraper.py

# Run only keyword scraping
python3 scraper.py -l

# Run only listing scraping
python3 scraper.py -d
```

## Data Files

The scraper generates two JSON files:

- `data/course_listings.json` - Contains basic course listing information
- `data/data.json` - Contains detailed course information

## Dependencies

- requests
- beautifulsoup4
- tqdm
- lxml

## Notes

- The scraper handles pagination for search results
- It includes error handling for failed requests
- It avoids duplicate entries when updating data files 