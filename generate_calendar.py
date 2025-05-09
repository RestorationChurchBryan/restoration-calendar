        event = Event()
        event.name = title
        event.description = desc
        event.begin = raw_date
        calendar.events.add(event)
    except Exception as e:
        print(f"Skipping one block due to error: {e}")

with open('restoration_church_calendar.ics', 'w') as f:
    f.writelines(calendar)
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event

url = 'https://restorationbryan.com/events'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

calendar = Calendar()

# Updated: looks for each event block under a known Elementor structure
event_blocks = soup.select('article.elementor-post')

print(f"Found {len(event_blocks)} event blocks")
for block in event_blocks:
    try:
        title = block.select_one('.elementor-post__title').text.strip()
        desc = block.select_one('.elementor-post__excerpt').text.strip()
        raw_date = block.select_one('time').get('datetime')  # ISO 8601 format

        event = Event()
        event.name = title
        event.description = desc
        event.begin = raw_date
        calendar.events.add(event)
    except Exception as e:
        print(f"Skipping one block due to error: {e}")

with open('restoration_church_calendar.ics', 'w') as f:
    f
import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event

url = 'https://restorationbryan.com/events'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

calendar = Calendar()

# Updated: looks for each event block under a known Elementor structure
event_blocks = soup.select('article.elementor-post')

for block in event_blocks:
    try:
        title = block.select_one('.elementor-post__title').text.strip()
        desc = block.select_one('.elementor-post__excerpt').text.strip()
        raw_date = block.select_one('time').get('datetime')  # ISO 8601 format

        event = Event()
        event.name = title
        event.description = desc
        event.begin = raw_date
        calendar.events.add(event)
    except Exception as e:
        print(f"Skipping one block due to error: {e}")

with open('restoration_church_calendar.ics', 'w') as f:
    f

