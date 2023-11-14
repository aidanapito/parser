from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrapeTeamStats_SouthernVirginia(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)

    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, 'html.parser')

    # Find all rows with class 'odd' or 'even' within both the offensive and defensive sections
    all_player_rows = soup.select('section#individual-overall-offensive table.sidearm-table tbody tr.odd, section#individual-overall-offensive table.sidearm-table tbody tr.even, section#individual-overall-defensive table.sidearm-table tbody tr.odd, section#individual-overall-defensive table.sidearm-table tbody tr.even')

    # Initialize empty lists to store player data for offense and defense
    player_data_offense = []
    player_data_defense = []

    # Iterate through player rows and extract information for offense and defense
    for row in all_player_rows:
        # Extract the player's name
        full_name = row.select_one('td:nth-of-type(2)').text.strip().split('\n')[0]

        # Check if the full name is in the expected format
        if ', ' in full_name:
            first_name, last_name = full_name.split(', ')
            name = f'{first_name} {last_name}'
        else:
            # Handle the case where the full name is not in the expected format
            name = full_name

        # Determine whether the row belongs to offense or defense
        if any('offensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            # This is an offense row
            jersey_number = row.select_one('td:nth-of-type(1)').text.strip()
            # Extract other columns for offense

            # Combine the data into a single list for offense
            player_info_offense = [name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_offense.append(player_info_offense)

        elif any('defensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            # This is a defense row
            jersey_number = row.select_one('td:nth-of-type(1)').text.strip()
            # Extract other columns for defense

            # Combine the data into a single list for defense
            player_info_defense = [name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_defense.append(player_info_defense)

    # Create separate DataFrames for offense and defense with specified columns
    offense_columns = ['Name', 'Jersey Number', 'Sets Played', 'Matches Played', 'Matches Started',
                    'Points', 'Points/Set', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts',
                    'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces',
                    'Services Aces/Set', 'Service Errors', 'ViewBio']
    defense_columns = ['Name', 'Jersey Number', 'Sets Played', 'Digs', 'Digs/Set', 'Reception Error',
                    'Total Reception Attempts', 'Reception Percentage', 'Reception Errors/Set',
                    'Solo Blocks', 'Block Assist', 'Block Points', 'Blocks/Set', 'Block Errors',
                    'BHE', 'ViewBio']

    # Initialize empty DataFrames with specified columns
    dfSouthernVirginiaOffense = pd.DataFrame(columns=offense_columns)
    dfSouthernVirginiaDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfSouthernVirginiaOffense = pd.concat([dfSouthernVirginiaOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfSouthernVirginiaDefense = pd.concat([dfSouthernVirginiaDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfSouthernVirginiaDefense = dfSouthernVirginiaDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfSouthernVirginiaOffense = dfSouthernVirginiaOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfSouthernVirginiaCombinedStats = pd.concat([dfSouthernVirginiaOffense, dfSouthernVirginiaDefense], axis=1)

    # Set the index to 'SouthernVirginia' for all rows
    dfSouthernVirginiaCombinedStats['Team'] = 'SouthernVirginia'
    dfSouthernVirginiaCombinedStats.set_index('Team', inplace=True)

    dfSouthernVirginiaCombinedStats.to_csv('SouthernVirginiaCombinedStats.csv', header=False)

    return dfSouthernVirginiaCombinedStats

scrapeTeamStats_SouthernVirginia('https://knightathletics.com/sports/mens-volleyball/stats')