from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

url = 'https://rutgersnewarkathletics.com/sports/mens-volleyball/stats'
driver = webdriver.Chrome()
driver.get(url)
time.sleep(5)

page_source = driver.page_source
driver.quit()
soup = BeautifulSoup(page_source, 'html.parser')

# Find all rows with class 'odd' or 'even' within the 'individual-overall-defensive' section
player_rows = soup.select('section#individual-overall-defensive table.sidearm-table tbody tr.odd, section#individual-overall-defensive table.sidearm-table tbody tr.even')

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

    # Extract only the relevant columns for defensive statistics
    player_info = [name, jersey_number] + [column.text.strip() for column in columns]
    player_data.append(player_info)

# Create a DataFrame from the extracted data
dfRutgersNewark = pd.DataFrame(player_data)

# Rename columns for better readability
dfRutgersNewark.columns = ['Name', 'Jersey Number', 'Sets Played', 'Digs', 'Digs/Set', 'Reception Error', 'Total Reception Attempts', 'Reception Percentage', 'Reception Errors/Set', 'Solo Blocks', 'Block Assist', 'Block Points', 'Blocks/Set', 'Block Errors', 'BHE', 'ViewBio']


# Drop 'ViewBio' from being parsed
dfRutgersNewark = dfRutgersNewark.drop("ViewBio", axis=1)


# Set the index to 'RUTGERS' for all rows
dfRutgersNewark['Team'] = 'RUTGERS'
dfRutgersNewark.set_index('Team', inplace=True)

# Print the DataFrame
print(dfRutgersNewark)





