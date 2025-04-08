from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from ics import Calendar, Event
from dateutil import parser as dateparser
from datetime import datetime   # Added import for datetime
import time

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# Load the Subsplash embed page
driver.get("https://subsplash.com/+t3nc/lb/ca/+m29p32p?embed&branding")

# Wait until at least one event title is visible
WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "h2.kit-list-item__title"))
)
print("Initial events loaded.")

prev_count = 0
while True:
    time.sleep(3)  # Pause to let new events load
    current_html = driver.page_source
    soup_current = BeautifulSoup(current_html, "html.parser")
    current_events = soup_current.select(".kit-list-item")
    current_count = len(current_events)
    print(f"After pagination, found {current_count} events.")
    
    # Stop if no new events are loaded
    if current_count <= prev_count:
        print("No new events loaded. Ending pagination.")
        break
    prev_count = current_count

    try:
        # Click the right arrow using a CSS selector that targets the outer <div>
        arrow = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.kit-pagination__page.kit-pagination__page--arrow.kit-pagination__arrow--right"))
        )
        print("Clicking right arrow...")
        driver.execute_script("arguments[0].click();", arrow)
    except Exception as e:
        print("Arrow not clickable: ", e)
        break

# Extra wait for final events to load
time.sleep(5)
html = driver.page_source
driver.quit()

# Save final snapshot for debugging (optional)
with open("subsplash_final_snapshot.html", "w") as f:
    f.write(html)

soup = BeautifulSoup(html, "html.parser")
event_blocks = soup.select(".kit-list-item")
print(f"Final total events found: {len(event_blocks)}")

calendar = Calendar()

for i, block in enumerate(event_blocks):
    try:
        title = block.select_one(".kit-list-item__title").get_text(strip=True)
        datetime_str = block.select_one(".kit-list-item__subtitle").get_text(strip=True)
        desc_tag = block.select_one(".kit-list-item__summary")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description provided."

        # Expected format: "April 8, 2025 from 6:30 to 7:30am" (or with a hyphen)
        if " from " in datetime_str:
            parts = datetime_str.split(" from ")
            if len(parts) != 2:
                print(f"Skipping event {i}: Unexpected datetime format '{datetime_str}'")
                continue
            date_part, time_range = parts
            # Use the start time from the range.
            # This assumes time_range could be in the format "6:30 to 7:30am" or "6:30 - 7:30am"
            if " to " in time_range:
                start_time = time_range.split(" to ")[0].strip()
            elif " - " in time_range:
                start_time = time_range.split(" - ")[0].strip()
            else:
                start_time = time_range.strip()
            start_dt_str = f"{date_part} {start_time}"
        else:
            # If there's no ' from ', assume it's just a date and use a default time.
            start_dt_str = f"{datetime_str.strip()} 09:00 AM"

        try:
            start = dateparser.parse(start_dt_str)
        except Exception as parse_error:
            print(f"Skipping event {i} due to date parsing error: {parse_error}")
            continue

        event = Event()
        event.name = title
        event.begin = start
        event.description = description
        # Set DTSTAMP to current UTC time so the event has a creation timestamp.
        event.dtstamp = datetime.utcnow()
        calendar.events.add(event)

    except Exception as e:
        print(f"Skipping event {i} due to error: {e}")

# Save the final iCalendar (.ics) file
with open("restoration_church_calendar.ics", "w") as f:
    f.writelines(calendar)
