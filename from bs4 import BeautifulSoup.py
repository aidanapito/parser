from bs4 import BeautifulSoup
import pandas as pd
import requests

source = requests.get('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats')

soup = BeautifulSoup(source.text, 'html.parser')

soup.find_all("tr", class_ ="odd")
soup.find_all("tr", class_ ="even")

Players= int
df = pd.DataFrame(Players, columns = ['Position','Matches Played','Sets Played','Kills','Kills per Set','Attack Errors','Total Attacking Attempts', 'Hitting Percentage', 'Assists','Assists per Set','Service Aces', 'Service Aces per Set', 'Service Errors'])
print (df)