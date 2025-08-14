import json
from bs4 import BeautifulSoup
from tqdm import tqdm
from scrape_listings_by_keyword import fetch

def extract_class_details(soup):
    header = soup.find("h1").text.strip()
    parts = header.strip().split(":", 1)
    dept_code, course_title = parts[0].split("-"), parts[1].strip()

    course_dept, course_code, class_section = dept_code[0], dept_code[1], dept_code[2].strip()
    return course_dept, course_code, class_section, course_title

def extract_other_details(soup):
    details_table = soup.find("table", class_="nameValueTable")
    
    # left side details
    school = details_table.find("td", string="School:").find_next_sibling("td").text.strip()
    career = details_table.find("td", string="Career:").find_next_sibling("td").text.strip()
    class_type = details_table.find("td", string="Component:").find_next_sibling("td").text.strip()
    credit_hours = details_table.find("td", string="Hours:").find_next_sibling("td").text.strip()
    grading_basis = details_table.find("td", string="Grading Basis:").find_next_sibling("td").text.strip()
    consent = details_table.find("td", string="Consent:").find_next_sibling("td").text.strip()

    # right side details
    term = details_table.find("td", string="Term:").find_next_sibling("td").text.strip()
    term_year, term_season = term.split(" ")
    session = details_table.find("td", string="Session:").find_next_sibling("td").text.strip()
    dates = details_table.find("td", string="Session Dates:").find_next_sibling("td").text.strip()
    requirements = details_table.find("td", string="Requirement(s):").find_next_sibling("td").text.strip()

    return school, career, class_type, credit_hours, grading_basis, consent, term_year, term_season, session, dates, requirements

def extract_desc_and_notes(soup):
    description_div = soup.find("div", class_="detailHeader", string=lambda text: "Description" in text)
    description = description_div.find_next_sibling("div").text.strip() if description_div else None

    notes_div = soup.find("div", class_="detailHeader", string=lambda text: "Notes" in text)
    notes = notes_div.find_next_sibling("div").text.strip() if notes_div else None

    return description, notes

def extract_availability(soup):
    availability_table = soup.find("table", class_="availabilityNameValueTable")
    status = soup.find("div", class_="availabiltyIndicator").find("span").text.strip()
    capacity = availability_table.find("td", string="Class Capacity:").find_next_sibling("td").text.strip()
    enrolled = availability_table.find("td", string="Total Enrolled:").find_next_sibling("td").text.strip()
    wl_capacity = availability_table.find("td", string="Wait List Capacity:").find_next_sibling("td").text.strip()
    wl_occupied = availability_table.find("td", string="Total on Wait List:").find_next_sibling("td").text.strip()

    return status, capacity, enrolled, wl_capacity, wl_occupied

def extract_attributes(soup):
    attributes_div = soup.find("div", class_="detailHeader", string=lambda text: "Attributes" in text)
    attributes = [item.text.strip() for item in attributes_div.find_next_sibling("div").find_all("div", class_="listItem")] if attributes_div else None
    return attributes

def extract_meetings_and_instructors(soup):
    meeting_tables = soup.find_all("table", class_="meetingPatternTable")

    meeting_days = []
    meeting_times = []
    meeting_dates = []
    instructors = set()

    for meeting_table in meeting_tables:
        for row in meeting_table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if len(columns) < 4: continue # probably bad data
            meeting_days.append(columns[0].text.strip())
            meeting_times.append(columns[1].text.strip())
            meeting_dates.append(columns[3].text.strip())
            for inst in columns[4].find_all("div"): instructors.add(inst.text.strip())

    return meeting_days, meeting_times, meeting_dates, list(instructors)

def scrape_course_details(soup, term_code):
    class_number = soup.find("div", class_="classNumber").text.split(":")[1].strip()
    course_dept, course_code, class_section, course_title = extract_class_details(soup)
    school, career, class_type, credit_hours, grading_basis, consent, term_year, term_season, session, dates, requirements = extract_other_details(soup)
    description, notes = extract_desc_and_notes(soup)
    status, capacity, enrolled, wl_capacity, wl_occupied = extract_availability(soup)
    attributes = extract_attributes(soup)
    meeting_days, meeting_times, meeting_dates, instructors = extract_meetings_and_instructors(soup)
    
    current_data = {
        "id": "cn" + class_number + "tc" + term_code,
        "course_dept": course_dept,
        "course_code": course_code,
        "class_section": class_section,
        "course_title": course_title,
        "school": school,
        "career": career,
        "class_type": class_type,
        "credit_hours": credit_hours,
        "grading_basis": grading_basis,
        "consent": consent,
        "term_year": term_year,
        "term_season": term_season,
        "session": session,
        "dates": dates,
        "requirements": requirements,
        "description": description,
        "notes": notes,
        'status': status,
        'capacity': capacity,
        'enrolled': enrolled,
        'wl_capacity': wl_capacity,
        'wl_occupied': wl_occupied,
        "attributes": attributes,
        "meeting_days": meeting_days,
        "meeting_times": meeting_times, 
        "meeting_dates": meeting_dates, 
        "instructors": instructors
    }

    return current_data

def update_course_details(new_data):
    # load existing data
    try:
        with open('data/data.json', 'r') as file:
            existing_data = json.load(file)
    except FileNotFoundError:
        existing_data = []
    
    # convert to dict for easy saving
    existing_data_dict = {entry["id"]: entry for entry in existing_data}
    id = new_data["id"]
    existing_data_dict[id] = new_data # update or append

    # back to list for saving
    updated_data = list(existing_data_dict.values())
    
    with open('data/data.json', 'w') as file:
        json.dump(updated_data, file, indent=4)

def iterate_listings():
    with open('data/course_listings.json', 'r') as file:
        data = json.load(file)
    
    base_url = "https://more.app.vanderbilt.edu/more/GetClassSectionDetail.action?classNumber="
    for listing in tqdm(data, desc="Scraping data", unit="listing"):
        url = base_url + f"{listing['classNumber']}&termCode={listing['termCode']}"
        try:
            soup = fetch(url)
            current_data = scrape_course_details(soup, listing['termCode'])
            update_course_details(current_data)
        except:
            print(f"error scraping details for listing '{listing}'") 
        
        try:
            soup = fetch(url)
        except:
            print("1")

        try:
            current_data = scrape_course_details(soup, listing['termCode'])
        except:
            print("2")

        try:
            update_course_details(current_data)
        except:
            print("3")