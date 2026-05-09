"""To test webscraber"""

import requests
from bs4 import BeautifulSoup


url = "https://www.parkrun.co.at/stadtparkgraz/results/eventhistory/"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

rows = soup.find_all('tr', class_='Results-table-row')

event_data = []

for row in rows:
    # Use .get() to pull data directly from the attributes
    # This avoids navigating the messy <span> and <div> tags inside
    data = {
        'event_number': row.get('data-parkrun'),
        'date': row.get('data-date'),
        'finishers': row.get('data-finishers'),
        'volunteers': row.get('data-volunteers'),
        'first_male': row.get('data-male'),
        'male_time': row.get('data-maletime'),
        'first_female': row.get('data-female'),
        'female_time': row.get('data-femaletime')
    }
    event_data.append(data)

# Example output for the first row found:
# {'event_number': '123', 'date': '2026-03-21', 'finishers': '68', ...}
print(event_data[0])