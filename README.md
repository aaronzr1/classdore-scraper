# Classdore Scraper

Scrapes course information from Vanderbilt University's course catalog and uploads it to Redis.

## File Structure

- `scraper.py` - Entry point with CLI arguments
    - calls `listings.py` - Keyword-based scraping to discover course listings
    - calls `details.py` - Scrapes detailed info for each discovered course
- `upload_to_redis.py` - Uploads scraped data to Redis with search indexing
- `.github/workflows/scrape.yml` - GitHub Actions workflow that wraps it all together

## Usage

```bash
# Scrape both listings and course details
python scraper.py

# Only scrape listings
python scraper.py -l

# Only scrape course details from discovered listings
python scraper.py -d

# Adjust concurrency and batch size
python scraper.py -c 8 -b 500
```

## Scheduling (GitHub Actions)

All scraping runs via GitHub Actions (`.github/workflows/scrape.yml`) on the `data-pipeline` branch:

- **Daily full scrape** at 3:30 AM CT (8:30 UTC) — regenerates listings, then scrapes details
- **Hourly delta scrape** — scrapes details only using existing listings (with a random delay to spread load)

After scraping, the workflow uploads results to Redis and commits `data/` to the `data-pipeline` branch.

## Data Files

The scraper generates two JSON files (stored on the `data-pipeline` branch):

- `data/course_listings.json` - Basic course listing info (class number, term code, keyword)
- `data/data.json` - Full course details (enrollment, schedule, instructors, etc.)

## Known Limitations

- Courses matching `*999` are skipped because 7999, 8999, and 9999 each return 300+ results, which overflow the paginator. These are mostly PhD dissertation research courses.
