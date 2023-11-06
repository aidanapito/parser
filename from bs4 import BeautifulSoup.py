from bs4 import BeautifulSoup
import pandas as pd
import requests

source = requests.get('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats')

soup = BeautifulSoup(source.text, 'html.parser')

odd_rows = soup.find_all("tr", class_="odd")
even_rows = soup.find_all("tr", class_="even")


dataRutgersNewark = []

for row in odd_rows + even_rows:
    columns = row.find_all("td")
    if len(columns) == 13:
        player_data = {
            'Position': columns[0].text.strip(),
            'Matches Played': int(columns[1].text.strip()),
            'Sets Played': int(columns[2].text.strip()),
            'Kills': int(columns[3].text.strip()),
            'Kills per Set': float(columns[4].text.strip()),
            'Attack Errors': int(columns[5].text.strip()),
            'Total Attacking Attempts': int(columns[6].text.strip()),
            'Hitting Percentage': float(columns[7].text.strip()),
            'Assists': int(columns[8].text.strip()),
            'Assists per Set': float(columns[9].text.strip()),
            'Service Aces': int(columns[10].text.strip()),
            'Service Aces per Set': float(columns[11].text.strip()),
            'Service Errors': int(columns[12].text.strip()),
        }
        dataRutgersNewark.append(player_data)
df = pd.DataFrame(dataRutgersNewark)
df