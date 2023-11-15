from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

 #CVC START
def scrapeTeamStats_RutgersNewark(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(5)

    page_source = driver.page_source
    driver.quit()
    soup = BeautifulSoup(page_source, 'html.parser')

    # -------------------------------------OFFENSE ---------------------------------------
    # Find all rows with class 'odd' or 'even' within the 'individual-overall-offensive' section
    player_rows_offense = soup.select(
        'section#individual-overall-offensive table.sidearm-table tbody tr.odd, section#individual-overall-offensive table.sidearm-table tbody tr.even')

    # Initialize an empty list to store player data
    player_data_offense = []

    # Iterate through player rows and extract information
    for row in player_rows_offense:
        # Extract the 'Jersey Number' column
        jersey_number = row.select_one('td:nth-of-type(1)').text.strip()

        # Extract the 'Name' column and split into first and last names
        full_name = row.select_one('td:nth-of-type(2)').text.strip().split('\n')[0]
        last_name, first_name = full_name.split(', ')
        name = f'{first_name} {last_name}'

        # Extract all other columns in the row
        columns = row.find_all('td')[2:]

        # Extract only the relevant columns for player statistics
        player_info = [name] + [jersey_number] + [column.text.strip() for column in columns]
        player_data_offense.append(player_info)

    dfRutgersNewarkOffense = pd.DataFrame(player_data_offense)

    # Rename columns for better readability
    dfRutgersNewarkOffense.columns = ['Name', 'Jersey Number', 'Sets Played', 'Matches Played', 'Matches Started',
                                      'Points', 'Points/Set', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts',
                                      'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces',
                                      'Services Aces/Set', 'Service Errors', 'ViewBio']

    # Drop 'ViewBio' from being parsed
    dfRutgersNewarkOffense = dfRutgersNewarkOffense.drop("ViewBio", axis=1)

    # Set the index to 'RUTGERS' for all rows
    dfRutgersNewarkOffense['Team'] = 'RUTGERS'
    dfRutgersNewarkOffense.set_index('Team', inplace=True)

    # -------------------------------DEFENSE--------------------------------------
    # Find all rows with class 'odd' or 'even' within the 'individual-overall-defensive' section

    player_rows_defense = soup.select(
        'section#individual-overall-defensive table.sidearm-table tbody tr.odd, section#individual-overall-defensive table.sidearm-table tbody tr.even')

    player_data_defense = []

    # Iterate through player rows and extract information
    for row in player_rows_defense:
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
        player_data_defense.append(player_info)

    # Create a DataFrame from the extracted data
    dfRutgersNewarkDefense = pd.DataFrame(player_data_defense)

    # Rename columns for better readability
    dfRutgersNewarkDefense.columns = ['Name', 'Jersey Number', 'Sets Played', 'Digs', 'Digs/Set', 'Reception Error',
                                      'Total Reception Attempts', 'Reception Percentage', 'Reception Errors/Set',
                                      'Solo Blocks', 'Block Assist', 'Block Points', 'Blocks/Set', 'Block Errors',
                                      'BHE', 'ViewBio']

    # Drop viewbio, name, jersey number, and sets played from being parsed on defense
    dfRutgersNewarkDefense = dfRutgersNewarkDefense.drop("ViewBio", axis=1)
    dfRutgersNewarkDefense = dfRutgersNewarkDefense.drop("Name", axis=1)
    dfRutgersNewarkDefense = dfRutgersNewarkDefense.drop("Jersey Number", axis=1)
    dfRutgersNewarkDefense = dfRutgersNewarkDefense.drop("Sets Played", axis=1)

    # Set the index to 'RUTGERS' for all rows
    dfRutgersNewarkDefense['Team'] = 'RUTGERS'
    dfRutgersNewarkDefense.set_index('Team', inplace=True)


    #combine both dataframes
    dfRutgersNewarkedCombinedStats = pd.concat([dfRutgersNewarkOffense, dfRutgersNewarkDefense], axis=1)
    dfRutgersNewarkedCombinedStats.reset_index(inplace=True)

    dfRutgersNewarkedCombinedStats.to_csv('RutgersNewarkCombinedStats.csv', index=False)

    return dfRutgersNewarkedCombinedStats
scrapeTeamStats_RutgersNewark('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats')
#------------------------------------------------------------------RutgersNewarkDONE------------------------------------------------------------------

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
#------------------------------------------------------------------SVU DONE------------------------------------------------------------------

def scrapeTeamStats_Kean(url):
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
    dfKeanOffense = pd.DataFrame(columns=offense_columns)
    dfKeanDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfKeanOffense = pd.concat([dfKeanOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfKeanDefense = pd.concat([dfKeanDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfKeanDefense = dfKeanDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfKeanOffense = dfKeanOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfKeanCombinedStats = pd.concat([dfKeanOffense, dfKeanDefense], axis=1)

    # Set the index to 'Kean' for all rows
    dfKeanCombinedStats['Team'] = 'Kean'
    dfKeanCombinedStats.set_index('Team', inplace=True)

    dfKeanCombinedStats.to_csv('KeanCombinedStats.csv', header=False)

    return dfKeanCombinedStats
scrapeTeamStats_Kean('https://keanathletics.com/sports/mens-volleyball/stats/2023') #change to 2024
#------------------------------------------------------------------KEAN DONE ------------------------------------------------------------------

def scrapeTeamStats_Marymount(url):
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
    dfMarymountOffense = pd.DataFrame(columns=offense_columns)
    dfMarymountDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfMarymountOffense = pd.concat([dfMarymountOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfMarymountDefense = pd.concat([dfMarymountDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfMarymountDefense = dfMarymountDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfMarymountOffense = dfMarymountOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfMarymountCombinedStats = pd.concat([dfMarymountOffense, dfMarymountDefense], axis=1)

    # Set the index to 'Marymount' for all rows
    dfMarymountCombinedStats['Team'] = 'Marymount'
    dfMarymountCombinedStats.set_index('Team', inplace=True)

    dfMarymountCombinedStats.to_csv('MarymountCombinedStats.csv', header=False)

    return dfMarymountCombinedStats
scrapeTeamStats_Marymount('https://marymountsaints.com/sports/mens-volleyball/stats')
#-------------------------------------------------------------------Marymount Done---------------------------------------------------------

def scrapeTeamStats_RandolphMacon(url):
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
    dfRandolphMaconOffense = pd.DataFrame(columns=offense_columns)
    dfRandolphMaconDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfRandolphMaconOffense = pd.concat([dfRandolphMaconOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfRandolphMaconDefense = pd.concat([dfRandolphMaconDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfRandolphMaconDefense = dfRandolphMaconDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfRandolphMaconOffense = dfRandolphMaconOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfRandolphMaconCombinedStats = pd.concat([dfRandolphMaconOffense, dfRandolphMaconDefense], axis=1)

    # Set the index to 'RandolphMacon' for all rows
    dfRandolphMaconCombinedStats['Team'] = 'RandolphMacon'
    dfRandolphMaconCombinedStats.set_index('Team', inplace=True)

    dfRandolphMaconCombinedStats.to_csv('RandolphMaconCombinedStats.csv', header=False)

    return dfRandolphMaconCombinedStats
scrapeTeamStats_RandolphMacon('https://rmcathletics.com/sports/mens-volleyball/stats/2023') #change to 2024
#--------------------------------------------------------------------RandolphMacon Done ----------------------------------------------------------

def scrapeTeamStats_Roanoke(url):
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
    dfRoanokeOffense = pd.DataFrame(columns=offense_columns)
    dfRoanokeDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfRoanokeOffense = pd.concat([dfRoanokeOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfRoanokeDefense = pd.concat([dfRoanokeDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfRoanokeDefense = dfRoanokeDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfRoanokeOffense = dfRoanokeOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfRoanokeCombinedStats = pd.concat([dfRoanokeOffense, dfRoanokeDefense], axis=1)

    # Set the index to 'Roanoke' for all rows
    dfRoanokeCombinedStats['Team'] = 'Roanoke'
    dfRoanokeCombinedStats.set_index('Team', inplace=True)

    dfRoanokeCombinedStats.to_csv('RoanokeCombinedStats.csv', header=False)

    return dfRoanokeCombinedStats
scrapeTeamStats_Roanoke('https://roanokemaroons.com/sports/mens-volleyball/stats') 
#-----------------------------------------------------------------------RoanokeDone------------------------------------------------------

def scrapeTeamStats_Elizabethtown(url):
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
    dfElizabethtownOffense = pd.DataFrame(columns=offense_columns)
    dfElizabethtownDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfElizabethtownOffense = pd.concat([dfElizabethtownOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfElizabethtownDefense = pd.concat([dfElizabethtownDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfElizabethtownDefense = dfElizabethtownDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfElizabethtownOffense = dfElizabethtownOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfElizabethtownCombinedStats = pd.concat([dfElizabethtownOffense, dfElizabethtownDefense], axis=1)

    # Set the index to 'Elizabethtown' for all rows
    dfElizabethtownCombinedStats['Team'] = 'Elizabethtown'
    dfElizabethtownCombinedStats.set_index('Team', inplace=True)

    dfElizabethtownCombinedStats.to_csv('ElizabethtownCombinedStats.csv', header=False)

    return dfElizabethtownCombinedStats
scrapeTeamStats_Elizabethtown('https://etownbluejays.com/sports/mens-volleyball/stats/2023#individual') #change
#----------------------------------------------------------------------Elizabethtown Done----------------------------------------------------------

dfRutgersNewarkedCombinedStats = scrapeTeamStats_RutgersNewark('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats')
dfSouthernVirginiaCombinedStats = scrapeTeamStats_SouthernVirginia('https://knightathletics.com/sports/mens-volleyball/stats')
dfKeanCombinedStats = scrapeTeamStats_Kean('https://keanathletics.com/sports/mens-volleyball/stats/2023') #Change to 2024 when new season starts
dfMarymountCombinedStats = scrapeTeamStats_Marymount('https://marymountsaints.com/sports/mens-volleyball/stats')
dfRandolphMaconCombinedStats = scrapeTeamStats_RandolphMacon('https://rmcathletics.com/sports/mens-volleyball/stats/2023') #change to 2024 when new season starts
dfRoanokeCombinedStats = scrapeTeamStats_Roanoke('https://roanokemaroons.com/sports/mens-volleyball/stats')
dfElizabethtownCombinedStats = scrapeTeamStats_Elizabethtown('https://etownbluejays.com/sports/mens-volleyball/stats/2023#individual') #change
#CVC END

#UVC START
def scrapeTeamStats_MIT(url):
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
    dfMITOffense = pd.DataFrame(columns=offense_columns)
    dfMITDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfMITOffense = pd.concat([dfMITOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfMITDefense = pd.concat([dfMITDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfMITDefense = dfMITDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfMITOffense = dfMITOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfMITCombinedStats = pd.concat([dfMITOffense, dfMITDefense], axis=1)

    # Set the index to 'MIT' for all rows
    dfMITCombinedStats['Team'] = 'MIT'
    dfMITCombinedStats.set_index('Team', inplace=True)

    dfMITCombinedStats.to_csv('MITCombinedStats.csv', header=False)

    return dfMITCombinedStats
scrapeTeamStats_MIT('https://mitathletics.com/sports/mens-volleyball/stats/2022') #change
#--------------------------------------------------------------------MIT DONE----------------------------------------------------------------------

def scrapeTeamStats_Nazareth(url):
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
    dfNazarethOffense = pd.DataFrame(columns=offense_columns)
    dfNazarethDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfNazarethOffense = pd.concat([dfNazarethOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfNazarethDefense = pd.concat([dfNazarethDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfNazarethDefense = dfNazarethDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfNazarethOffense = dfNazarethOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfNazarethCombinedStats = pd.concat([dfNazarethOffense, dfNazarethDefense], axis=1)

    # Set the index to 'Nazareth' for all rows
    dfNazarethCombinedStats['Team'] = 'Nazareth'
    dfNazarethCombinedStats.set_index('Team', inplace=True)

    dfNazarethCombinedStats.to_csv('NazarethCombinedStats.csv', header=False)

    return dfNazarethCombinedStats
scrapeTeamStats_Nazareth('https://nazathletics.com/sports/mens-volleyball/stats/2023#individual')  #change
#--------------------------------------------------------------------Nazareth DONE -----------------------------------------------------------------

def scrapeTeamStats_NYU(url):
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
    dfNYUOffense = pd.DataFrame(columns=offense_columns)
    dfNYUDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfNYUOffense = pd.concat([dfNYUOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfNYUDefense = pd.concat([dfNYUDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfNYUDefense = dfNYUDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfNYUOffense = dfNYUOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfNYUCombinedStats = pd.concat([dfNYUOffense, dfNYUDefense], axis=1)

    # Set the index to 'NYU' for all rows
    dfNYUCombinedStats['Team'] = 'NYU'
    dfNYUCombinedStats.set_index('Team', inplace=True)

    dfNYUCombinedStats.to_csv('NYUCombinedStats.csv', header=False)

    return dfNYUCombinedStats
scrapeTeamStats_NYU('https://gonyuathletics.com/sports/mens-volleyball/stats/2023')  #change
#-----------------------------------------------------------------------NYU DONE -----------------------------------------------------------------

def scrapeTeamStats_StJohnFisher(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(7)

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
    dfStJohnFisherOffense = pd.DataFrame(columns=offense_columns)
    dfStJohnFisherDefense = pd.DataFrame(columns=defense_columns)

    # Populate DataFrames with player data for offense and defense
    dfStJohnFisherOffense = pd.concat([dfStJohnFisherOffense, pd.DataFrame(player_data_offense, columns=offense_columns)], ignore_index=True)
    dfStJohnFisherDefense = pd.concat([dfStJohnFisherDefense, pd.DataFrame(player_data_defense, columns=defense_columns)], ignore_index=True)

    # Drop unnecessary columns from defense DataFrame
    dfStJohnFisherDefense = dfStJohnFisherDefense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)
    dfStJohnFisherOffense = dfStJohnFisherOffense.drop(["ViewBio"], axis=1)

    # Combine both DataFrames horizontally (next to each other)
    dfStJohnFisherCombinedStats = pd.concat([dfStJohnFisherOffense, dfStJohnFisherDefense], axis=1)

    # Set the index to 'StJohnFisher' for all rows
    dfStJohnFisherCombinedStats['Team'] = 'StJohnFisher'
    dfStJohnFisherCombinedStats.set_index('Team', inplace=True)

    dfStJohnFisherCombinedStats.to_csv('StJohnFisherCombinedStats.csv', header=False)

    return dfStJohnFisherCombinedStats
scrapeTeamStats_StJohnFisher('https://sjfathletics.com/sports/mens-volleyball/stats/2023')  #change
#----------------------------------------------------------------------------SJFISHER DONE -----------------------------------------------------------------



dfMITCombinedStats = scrapeTeamStats_MIT('https://mitathletics.com/sports/mens-volleyball/stats/2022') #change
dfNazarethCombinedStats = scrapeTeamStats_Nazareth('https://nazathletics.com/sports/mens-volleyball/stats/2023#individual') #change
dfNYUCombinedStats = scrapeTeamStats_NYU('https://gonyuathletics.com/sports/mens-volleyball/stats/2023') #change
dfStJohnFisherCombinedStats = scrapeTeamStats_StJohnFisher('https://stjohnfisher.com/sports/mens-volleyball/stats/2023') #change


#UVC END




def combineTeamStats(dfRutgersNewarkedCombinedStats, dfSouthernVirginiaCombinedStats, dfKeanCombinedStats, dfMarymountCombinedStats, dfRandolphMaconCombinedStats, dfRoanokeCombinedStats, dfElizabethtownCombinedStats, dfMITCombinedStats, dfNazarethCombinedStats, dfNYUCombinedStats,dfStJohnFisherCombinedStats):

    # Add a new column 'Team' with the respective team names
    dfRutgersNewarkedCombinedStats['Team'] = 'Rutgers Newark'
    dfSouthernVirginiaCombinedStats['Team'] = 'Southern Virginia'
    dfKeanCombinedStats['Team'] = 'KEAN'
    dfMarymountCombinedStats['Team'] = 'Marymount'
    dfRandolphMaconCombinedStats['Team'] = 'Randolph Macon'
    dfRoanokeCombinedStats['Team'] = 'Roanoke'
    dfElizabethtownCombinedStats['Team'] = 'Elizabethtown'
    dfMITCombinedStats['Team'] = 'MIT'
    dfNazarethCombinedStats['Team'] = 'Nazareth'
    dfNYUCombinedStats['Team'] = 'NYU'
    dfStJohnFisherCombinedStats['Team'] = 'St John Fisher'


    # Concatenate the DataFrames
    dfTOTALSTATS = pd.concat([dfRutgersNewarkedCombinedStats, dfSouthernVirginiaCombinedStats, dfKeanCombinedStats, dfMarymountCombinedStats, dfRandolphMaconCombinedStats, dfRoanokeCombinedStats, dfElizabethtownCombinedStats, dfMITCombinedStats, dfNazarethCombinedStats, dfNYUCombinedStats, dfStJohnFisherCombinedStats], ignore_index=True)

    # Save the combined DataFrame to a CSV file
    dfTOTALSTATS.to_csv('CombinedStats.csv', index=False)
    return dfTOTALSTATS

# Call the function with your DataFrames
dfTOTALSTATS = combineTeamStats(dfRutgersNewarkedCombinedStats, dfSouthernVirginiaCombinedStats, dfKeanCombinedStats, dfMarymountCombinedStats, dfRandolphMaconCombinedStats, dfRoanokeCombinedStats, dfElizabethtownCombinedStats, dfMITCombinedStats, dfNazarethCombinedStats, dfNYUCombinedStats, dfStJohnFisherCombinedStats)