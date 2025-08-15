import requests
import re
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

def find_total_records(soup):
    """
    A simple helper function to find total records that pop up for a given search result.

    Parameters:
    soup (BeautifulSoup object): 

    Returns:
    int: total number of records
    """
    script_tag = soup.find('script', string=re.compile('totalRecords'))

    total_records = 0
    if script_tag:
        match = re.search(r'totalRecords\s*:\s*(\d+)', script_tag.string)
        if match: 
            total_records = int(match.group(1))
    
    return total_records

def fetch(url):
    """
    A simple fetch function to extract data from a url (with search keywords encoded).

    Parameters:
    url (string): url to extract data from

    Returns:
    BeautifulSoup object: extracted info from url
    """
    session = requests.Session() # use same session to allow page switching

    response = session.get(url)
    content = response.content
    
    total_records = find_total_records(BeautifulSoup(content, "lxml"))
    if total_records == 300: 
        print("NOTE: MAX RECORD COUNT HIT WITH URL", url)

    # 0-50 records means no additional pages, 51-100 means 1 additional page, etc.
    additional_pages = max(0, total_records // 50 - (not (total_records % 50))) # note 0 gives -1
    page_url = "https://more.app.vanderbilt.edu/more/SearchClassesExecute!switchPage.action?pageNum="

    for i in range(additional_pages):
        add_response = session.get(page_url + str(i + 2))
        content += add_response.content
    
    soup = BeautifulSoup(content, "lxml")
    return soup

def scrape_listings_for_keyword(soup):
    # find all <td> with "classNumber_" in id
    listing_elements = soup.find_all('td', id=lambda x: x and x.startswith("classNumber_"))

    new_data = []
    for listing in listing_elements:
        onclick_text = listing.get('onclick', '')
        
        class_number, term_code = None, None
        if "classNumber" in onclick_text and "termCode" in onclick_text:
            class_number = onclick_text.split("classNumber : '")[1].split("'")[0]
            term_code = onclick_text.split("termCode : '")[1].split("'")[0]
        
        if class_number and term_code:
            new_data.append({'classNumber': class_number, 'termCode': term_code})
    
    return new_data

def update_course_listings(new_data):
    # load existing data
    try:
        with open('data/course_listings.json', 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []

    # duplicate detection
    existing_set = set((entry["classNumber"], entry["termCode"]) for entry in existing_data)

    # add unique entries
    for entry in new_data:
        pair = (entry["classNumber"], entry["termCode"])
        if pair not in existing_set:
            existing_data.append(entry)
            existing_set.add(pair)

    with open('data/course_listings.json', 'w') as file:
        json.dump(existing_data, file, indent=4)

def iterate_keywords():
    base_url = "https://more.app.vanderbilt.edu/more/SearchClassesExecute!search.action?keywords="

    edges = [100, 110, 385, 799, 850, 899] # keywords that have over 300 entries (gets truncated)
    # skip *999 series since it's mostly phd dissertation research (7999, 8999, 9999 have 300+ each)
    # for i in tqdm(range(999), desc="Generating course listings", unit="keyword"):
    for i in tqdm(range(5), desc="Generating course listings", unit="keyword"):

        if i in edges:
            addons = [str(j) + f"{i:03d}" for j in range(10)]
        else:
            addons = [f"{i:03d}"]

        for addon in addons:
            url = base_url + addon

            # response = requests.get(url)
            # content = response.content
            # total_records = find_total_records(BeautifulSoup(content, "lxml"))

            try:
                soup = fetch(url)
                new_data = scrape_listings_for_keyword(soup)
                update_course_listings(new_data)
            except:
                print(f"error scraping listings for keyword '{addon}'") 