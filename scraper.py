import argparse
from listings import iterate_keywords
from details import iterate_listings

def main():
    parser = argparse.ArgumentParser(description="Scrape course listings and details.")
    
    parser.add_argument('-l', '--listings', action='store_true', help="Scrape course listings only")
    parser.add_argument('-d', '--details', action='store_true', help="Scrape course details only")
    
    args = parser.parse_args()

    # If neither flag is passed, run both functions
    if not (args.listings or args.details):
        iterate_keywords()
        iterate_listings()
    else:
        if args.listings:
            iterate_keywords()

        if args.details:
            iterate_listings()

if __name__ == "__main__":
    main() 