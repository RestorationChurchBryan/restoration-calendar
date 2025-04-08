from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from ics import Calendar, Event
from dateutil import parser as dateparser
from datetime import datetime
import time

# Configuration
page_wait = 5
post_click_wait = 3

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

all_event_blocks = []

for page in range(1, 11):
    if page == 1:
        url = "https://subsplash.com/+t3nc/lb/ca/+m29p32p?embed&branding"
    else:
        url = f"https://subsplash.com/+t3nc/lb/ca/+m29p32p?branding=true&embed=true&page={page}"
    print(f"\nLoading page {page}: {url}")

    driver.get(url)
    time.sleep(page_wait)

    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")

    event_blocks = soup.select(".kit-list-item")
    count = len(event_blocks)
    print(f"Page {page}: Found {count} events.")

    if count == 0:
        print(f"No events found on page {page}. Stopping further pagination.")
        break

    all_event_blocks.extend(event_blocks)
    time.sleep(post_click_wait)

driver.quit()

print(f"\nTotal raw events before filtering: {len(all_event_blocks)}")
# No deduplication is performed — we keep every event block

calendar = Calendar()

for i, block in enumerate(all_event_blocks):
    try:
        title = block.select_one(".kit-list-item__title").get_text(strip=True)
        datetime_str = block.select_one(".kit-list-item__subtitle").get_text(strip=True)
        desc_tag = block.select_one(".kit-list-item__summary")
        description = desc_tag.get_text(strip=True) if desc_tag else "No description provided."

        if " from " in datetime_str:
            parts = datetime_str.split(" from ")
            if len(parts) != 2:
                print(f"Skipping event {i}: Unexpected datetime format '{datetime_str}'")
                continue
            date_part, time_range = parts
            if " to " in time_range:
                start_time = time_range.split(" to ")[0].strip()
            elif " - " in time_range:
                start_time = time_range.split(" - ")[0].strip()
            else:
                start_time = time_range.strip()
            start_dt_str = f"{date_part} {start_time}"
        else:
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
        event.dtstamp = datetime.utcnow()
        calendar.events.add(event)

    except Exception as e:
        print(f"Skipping event {i} due to error: {e}")


from datetime import datetime
from ics import Event

# Manually added Restoration events (originally from Excel)

event = Event()
event.name = "Restoration 1st Service"
event.begin = datetime(2025, 4, 13, 8, 45)
event.end = datetime(2025, 4, 13, 10, 15)
event.description = "Will be at 501 W 31st Street, Child care will be 4's and under, Overflow space on lawn, carpool if possible"
event.location = "501 W 31st Street Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 2nd Service"
event.begin = datetime(2025, 4, 13, 10, 45)
event.end = datetime(2025, 4, 13, 12, 0)
event.description = "Will be at 501 W 31st Street, Child care will be 4's and under, Overflow space on lawn, carpool if possible"
event.location = "502 W 31st Street Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 1st Service"
event.begin = datetime(2025, 4, 20, 8, 45)
event.end = datetime(2025, 4, 20, 10, 15)
event.description = "Easter @ Ice House, Childcare 6th grade & under"
event.location = "800 N Main St Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 2nd Service"
event.begin = datetime(2025, 4, 20, 10, 45)
event.end = datetime(2025, 4, 20, 12, 0)
event.description = "Easter @ Ice House, Childcare 6th grade & under"
event.location = "800 N Main St Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 1st Service"
event.begin = datetime(2025, 4, 27, 8, 45)
event.end = datetime(2025, 4, 27, 10, 15)
event.description = "Childcare 6th grade & under"
event.location = "800 N Main St Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 2nd Service"
event.begin = datetime(2025, 4, 27, 10, 45)
event.end = datetime(2025, 4, 27, 12, 0)
event.description = "Childcare 6th grade & under"
event.location = "800 N Main St Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 1st Service"
event.begin = datetime(2025, 5, 4, 8, 30)
event.end = datetime(2025, 5, 4, 9, 45)
event.description = "Move to 501, Child care 4's and under"
event.location = "501 W 31st Street Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 2nd Service"
event.begin = datetime(2025, 5, 4, 10, 0)
event.end = datetime(2025, 5, 4, 11, 15)
event.description = "Move to 501, Child care 4's and under"
event.location = "501 W 31st Street Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration 3rd Service"
event.begin = datetime(2025, 5, 4, 11, 30)
event.end = datetime(2025, 5, 4, 12, 45)
event.description = "Move to 501, Child care 4's and under"
event.location = "501 W 31st Street Bryan, TX 77803"
calendar.events.add(event)


event = Event()
event.name = "Restoration Service"
event.begin = datetime(2025, 5, 11, 10, 0)
event.end = datetime(2025, 5, 11, 11, 30)
event.description = "Services will be at 501 at 10 am the rest of the summer, child care is 4's and under"
event.location = "501 W 31st Street Bryan, TX 77803"
calendar.events.add(event)



# Confirm that 10 hardcoded events were added
hardcoded_event_count = sum(1 for e in calendar.events if (
    e.name and any(keyword in e.name for keyword in ["1st Service", "2nd Service"])
))

if hardcoded_event_count >= 10:
    print("\n✅ In addition to the events the program scraped, the 10 Sunday services leading to the new property have been added to the iCal.")

with open("restoration_church_calendar.ics", "w") as f:
    f.writelines(calendar)

print("\nCalendar file 'restoration_church_calendar.ics' has been created.")


# Final thank-you message in red
print("\033[91m" + "If anyone is finding this code, Tucker Ming spent too many hours making this before he graduated May 10, 2025, but he made this as a thank you to Restoration Church prior to his graduation during his time as the Communication Intern at Restoration. Thanks & Gig 'em -Tucker Ming '26 April 7, 2025" + "\033[0m")
