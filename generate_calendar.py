import requests
from bs4 import BeautifulSoup
from ics import Calendar, Event

url = 'https://restorationbryan.com/events'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

calendar = Calendar()

event_cards = soup.select('div.elementor-post')

for card in event_cards:
    try:
        title = card.select_one('.elementor-post__title').text.strip()
        desc = card.select_one('.elementor-post__excerpt').text.strip()
        raw_date = card.select_one('time').get('datetime')

        event = Event()
        event.name = title
        event.description = desc
        event.begin = raw_date
        calendar.events.add(event)
    except Exception as e:
        print(f"Skipping one card due to error: {e}")

with open('restoration_church_calendar.ics', 'w') as f:
    f.writelines(calendar)
