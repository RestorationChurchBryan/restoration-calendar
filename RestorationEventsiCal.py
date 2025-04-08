from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ics import Calendar, Event
import time
from dateutil import parser as dateparser

# Setup headless browser
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the actual embed page
driver.get("https://subsplash.com/+t3nc/lb/ca/+m29p32p?embed&branding")
time.sleep(10)  # Wait for JS to load everything

# Get the HTML and close
html = driver.page_source
driver.quit()

# Save a snapshot for debugging
with open("subsplash_final_snapshot.html", "w") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")
event_blocks = soup.select("div.kit-list-item")

print(f"Found {len(event_blocks)} events")

calendar = Calendar()

for i, block in enumerate(event_blocks):
    try:
        title = block.select_one("h2.kit-list-item__title").get_text(strip=True)
        datetime_str = block.select_one("h3.kit-list-item__subtitle").get_text(strip=True)
        description = block.select_one("p.kit-list-item__summary").get_text(strip=True)

        # Parse datetime from string like "April 13, 2025 from 6:00 - 7:30pm"
        date_part = datetime_str.split(" from ")[0]
        time_part = datetime_str.split(" from ")[1].split(" - ")[0]
        datetime_combined = f"{date_part} {time_part}"
        start_time = dateparser.parse(datetime_combined)

        event = Event()
        event.name = title
        event.description = description
        event.begin = start_time
        calendar.events.add(event)

    except Exception as e:
        print(f"Skipping event {i} due to error: {e}")

# Save calendar
with open("restoration_church_calendar.ics", "w") as f:
    f.writelines(calendar)
