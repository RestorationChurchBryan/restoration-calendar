import re
import time
from datetime import datetime, timedelta
from pytz import timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ics import Calendar, Event
from dateutil import parser as dateparser

# Configuration
page_wait = 5       # Seconds to wait for each page load
post_click_wait = 3 # Seconds to wait after each page load

# Define local timezone for Bryan, College Station (US/Central)
central_tz = timezone("US/Central")

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

all_event_blocks = []  # To store event blocks from each page

# Loop through pages 1 to 10 using explicit URL parameters.
for page in range(1, 11):
    if page == 1:
        url = "https://subsplash.com/+t3nc/lb/ca/+m29p32p?embed&branding"
    else:
        url = f"https://subsplash.com/+t3nc/lb/ca/+m29p32p?branding=true&embed=true&page={page}"
    print(f"\nLoading page {page}: {url}")
    driver.get(url)
    time.sleep(page_wait)  # Wait for page and its JS to load

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    
    event_blocks = soup.select(".kit-list-item")
    count = len(event_blocks)
    print(f"Page {page}: Found {count} events.")
    
    # If no events are found on this page, stop further pagination.
    if count == 0:
        print(f"No events found on page {page}. Stopping further pagination.")
        break
        
    all_event_blocks.extend(event_blocks)
    time.sleep(post_click_wait)

driver.quit()

# Remove duplicate events based on event title
unique_events = {}
for block in all_event_blocks:
    title_elem = block.select_one(".kit-list-item__title")
    if title_elem:
        title = title_elem.get_text(strip=True)
        unique_events[title] = block
all_event_blocks = list(unique_events.values())
print(f"\nTotal unique events found from pages: {len(all_event_blocks)}")

# Build the calendar
calendar = Calendar()

# Regular expression pattern to match expected datetime string.
# Expected example: "April 12, 2025 from 7:30 to 9:00pm CDT"
pattern = r'^(?P<date>[A-Za-z]+ \d{1,2}, \d{4}) from (?P<start>\d{1,2}:\d{2})(?:\s*(?P<period1>am|pm))?\s*(?:to|-)\s*(?P<end>\d{1,2}:\d{2})(?:\s*(?P<period2>am|pm))?(?:\s*(?P<tz>\S+))?'

for i, block in enumerate(all_event_blocks):
    try:
        title = block.select_one(".kit-list-item__title").get_text(strip=True)
        datetime_str = block.select_one(".kit-list-item__subtitle").get_text(strip=True)
        desc_tag = block.select_one(".kit-list-item__summary")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description provided."

        # Attempt to parse the datetime string using the regex.
        m = re.match(pattern, datetime_str, re.IGNORECASE)
        if m:
            date_part = m.group("date")
            start_time = m.group("start")
            period1 = m.group("period1")
            end_time = m.group("end")
            period2 = m.group("period2")
            tz = m.group("tz")
            # If start time lacks a period, use period2 if available.
            if not period1:
                period1 = period2 if period2 else ""
            # Construct start_dt_str
            start_dt_str = f"{date_part} {start_time} {period1}".strip()
            if tz:
                start_dt_str += f" {tz}"
            # Construct end_dt_str if end_time is provided.
            if end_time:
                end_dt_str = f"{date_part} {end_time} {period2}".strip() if period2 else f"{date_part} {end_time}"
                if tz:
                    end_dt_str += f" {tz}"
            else:
                end_dt_str = None
        else:
            # Fallback: if regex doesn't match, assume the entire string is a date and assign default time.
            start_dt_str = f"{datetime_str.strip()} 09:00 AM"
            end_dt_str = None

        try:
            start = dateparser.parse(start_dt_str)
        except Exception as parse_error:
            print(f"Skipping event {i} due to start date parsing error: {parse_error}")
            continue

        if end_dt_str:
            try:
                end = dateparser.parse(end_dt_str)
            except Exception as parse_error:
                print(f"Skipping event {i} due to end date parsing error: {parse_error}")
                continue
        else:
            # Default duration: one hour after start if end time is missing.
            end = start + timedelta(hours=1)

        # Force the parsed datetime into US/Central timezone if naive:
        if start.tzinfo is None:
            start = central_tz.localize(start)
        else:
            start = start.astimezone(central_tz)

        if end.tzinfo is None:
            end = central_tz.localize(end)
        else:
            end = end.astimezone(central_tz)

        event = Event()
        event.name = title
        event.begin = start
        event.end = end
        event.description = description
        event.dtstamp = datetime.utcnow()
        calendar.events.add(event)
    
    except Exception as e:
        print(f"Skipping event {i} due to error: {e}")

# Save the final iCalendar (.ics) file
with open("restoration_church_calendar.ics", "w") as f:
    f.writelines(calendar)

print("\nCalendar file 'restoration_church_calendar.ics' has been created.")
