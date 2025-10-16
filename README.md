# Classdore Scraper

This repo contains all the code used in extracting course information from Vanderbilt University's course catalog.

## Scraper

### File Structure

The scraper is organized into three main modules:

1. `listings.py` - Handles the keyword-based scraping to find course listings
2. `details.py` - Handles the scraping of course details for each registered listing
3. `scraping.py` - Entry point for the scraper with command-line arguments

### Usage

```bash
# Scrape both listings and course details
python3 scraper.py

# Only scrape listings
python3 scraper.py -l

# Only scrape course details from discovered listings
python3 scraper.py -d
```

### Implementation Notes

- The scraper handles pagination for search results
- It includes error handling for failed requests
- It gracefully handles existing entries when updating data files
- For now, we **do not** scrape for `*999` courses because I do not know how to deal with pagination (7999, 8999, and 9999 courses have 300+ listings each, which overflow the clickable page count). These courses should be mostly phd dissertation research courses anyways.

## Data Files

The scraper generates two JSON files:

- `data/course_listings.json` - Contains basic course listing information
- `data/data.json` - Contains detailed course information

For now, this data is uploaded only to the `data-pipeline` branch. This is just to keep things simple logistically when we hand off triggers for data scraping. We can manually sync the branches (`main` -> `data-pipeline` but not vice versa) by running `sync-NOTETHISWILLTRIGGERSCRAPING.sh`, though it will trigger scraping (with the -d flag).

## Triggers for Scraping

The trigger for scraping course listings (-l flag) is set for 8:30 UTC (3:30AM CT) daily. It is run by GitHub Actions, and the details on that are in `.github/workflows/listings.yml`. The generated course listings are uploaded to `data/course_listings.json` on the `data-pipeline` branch.

Scraping course details (-d flag) gets triggered on every **push** to the `data-pipeline` branch. This is handled by Fly.io: it creates a new deployment based on the contents of the `Dockerfile`, which as of now is set to run `railway.sh`. This scrapes course details and also calls `upload_to_redis.py` to upload the resulting `data/data.json` file to the Redis database.

`requirements.txt` is currently used to build containers for both triggers, this hasn't been an issue yet but splitting could be better practice.

**Temporary/Hacky Feature:** Right now, if a file named `UPLOAD_ONLY` is found in the root directory, the GitHub Workflow is set not to run. This means, normally, the Fly.io workflow to scrape for course details will not run either. However, if a sync is run on the `data-pipeline` branch Fly.io will still trigger, so the Fly.io deployment is set to only run `upload_to_redis.py` if that happens (no changes should be made to the database). ***Note*** that if you delete `UPLOAD_ONLY` from main, syncing won't delete it from `data-pipeline` (as of now).