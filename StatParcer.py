from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

url = 'https://rutgersnewarkathletics.com/sports/mens-volleyball/stats'
driver = webdriver.Chrome()
driver.get(url)

# Wait for the page to load
time.sleep(5)

# Get the page source after it's loaded
page_source = driver.page_source

driver.quit()

# BeautifulSoup to parse the page source
soup = BeautifulSoup(page_source, 'html.parser')

# Find all rows with class 'odd' or 'even' within the 'individual-overall-offensive' section
player_rows = soup.select('section#individual-overall-offensive table.sidearm-table tbody tr.odd, section#individual-overall-offensive table.sidearm-table tbody tr.even')

# Initialize an empty list to store player data
player_data = []

# Iterate through player rows and extract information
for row in player_rows:
    # Extract the 'Jersey Number' column
    jersey_number = row.select_one('td:nth-of-type(1)').text.strip()

    # Extract the 'Name' column and split into first and last names
    full_name = row.select_one('td:nth-of-type(2)').text.strip().split('\n')[0]
    first_name, last_name = full_name.split(', ')
    name = f'{first_name} {last_name}'

    # Extract all other columns in the row
    columns = row.find_all('td')[2:]

    # Extract only the relevant columns for player statistics
    player_info = [name] + [jersey_number] + [column.text.strip() for column in columns]
    player_data.append(player_info)

# Create a DataFrame from the extracted data
df = pd.DataFrame(player_data)

# Rename columns for better readability
df.columns = ['Name', 'Jersey Number', 'Sets Played', 'Matches Played', 'Matches Started', 'Points', 'Points/Set', 'Kills', 'Kills/Set' , 'Errors', 'Total Attempts', 'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces', 'Services Aces/Set', 'Service Errors', 'ViewBio']

# Drop 'ViewBio' from being parsed
df = df.drop("ViewBio", axis=1)

# Set the index to 'RUTGERS' for all rows
df['Team'] = 'RUTGERS'
df.set_index('Team', inplace=True)

# Display the modified DataFrame
print(df)

df.to_csv('RutgersNewarkIndividualStats.csv')