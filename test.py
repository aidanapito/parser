import time
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrapeTeamStats(url, team_name, output_filename, offensive_selector, defensive_selector):
    with webdriver.Chrome() as driver:
        driver.get(url)

        # Use an explicit wait for a specific element to be present on the page
        element_present = EC.presence_of_element_located((By.CSS_SELECTOR, offensive_selector))
        WebDriverWait(driver, 20).until(element_present)

        page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    all_player_rows = soup.select(f'{offensive_selector} tbody tr.odd, {offensive_selector} tbody tr.even, {defensive_selector} tbody tr.odd, {defensive_selector} tbody tr.even')

    player_data_offense_list = []
    player_data_defense_list = []

    for row in all_player_rows:
        full_name = row.select_one('td:nth-of-type(2)').text.strip().split('\n')[0]
        if ', ' in full_name:
            first_name, last_name = full_name.split(', ')
            name = f'{first_name} {last_name}'
        else:
            name = full_name

        jersey_number = row.select_one('td:nth-of-type(1)').text.strip()

        if any('offensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            player_data_offense = [name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_offense_list.append(player_data_offense)
        elif any('defensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            player_data_defense = [name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_defense_list.append(player_data_defense)

    offense_columns = ['Name', 'Jersey Number', 'Sets Played', 'Matches Played', 'Matches Started',
                        'Points', 'Points/Set', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts',
                        'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces',
                        'Services Aces/Set', 'Service Errors', 'ViewBio']
    defense_columns = ['Name', 'Jersey Number', 'Sets Played', 'Digs', 'Digs/Set', 'Reception Error',
                        'Total Reception Attempts', 'Reception Percentage', 'Reception Errors/Set',
                        'Solo Blocks', 'Block Assist', 'Block Points', 'Blocks/Set', 'Block Errors',
                        'BHE', 'ViewBio']

    df_offense = pd.DataFrame(player_data_offense_list, columns=offense_columns)
    df_defense = pd.DataFrame(player_data_defense_list, columns=defense_columns)

    # Drop unnecessary columns
    df_offense = df_offense.drop(["ViewBio"], axis=1)
    df_defense = df_defense.drop(["ViewBio", "Name", "Jersey Number", "Sets Played"], axis=1)

    # Concatenate the DataFrames
    df_combined_stats = pd.concat([df_offense, df_defense], axis=1)

    # Add 'Team' column
    df_combined_stats['Team'] = team_name

    # Set the index on the new DataFrame
    df_combined_stats.set_index('Team', inplace=True)

    # Save to CSV
    df_combined_stats.to_csv(output_filename, header=False)

    return df_combined_stats

# Create a list of team DataFrames

#NEED TO CHANGE ALL URLS WITH 2023 TO 2024!!!!

team_dfs = [

    #7 minutes to do 26 teams, should take about 30 minutes to run every team hopefully.

    #CVC
    scrapeTeamStats('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats', 'Rutgers Newark', 'RutgersNewarkCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://knightathletics.com/sports/mens-volleyball/stats', 'Southern Virginia', 'SouthernVirginiaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://keanathletics.com/sports/mens-volleyball/stats/2023', 'Kean', 'KeanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gonyuathletics.com/sports/mens-volleyball/stats/2023', 'NYU', 'NYUCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats', 'Rutgers Newark', 'RutgersNewarkCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://knightathletics.com/sports/mens-volleyball/stats', 'Southern Virginia', 'SouthernVirginiaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://keanathletics.com/sports/mens-volleyball/stats/2023', 'Kean', 'KeanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #Change to 2024 when new season starts
    scrapeTeamStats('https://marymountsaints.com/sports/mens-volleyball/stats', 'Marymount', 'MarymountCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table') ,
    scrapeTeamStats('https://rmcathletics.com/sports/mens-volleyball/stats/2023', 'Randolph Macon', 'RandolphMaconCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table') ,#change to 2024 when new season starts
    scrapeTeamStats('https://roanokemaroons.com/sports/mens-volleyball/stats', 'Roanoke', 'RoanokeCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), 
    scrapeTeamStats('https://etownbluejays.com/sports/mens-volleyball/stats/2023#individual', 'Elizabethtown', 'ElizabethtownCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change

    #UVC
    scrapeTeamStats('https://mitathletics.com/sports/mens-volleyball/stats/2022', 'MIT', 'MITCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    scrapeTeamStats('https://nazathletics.com/sports/mens-volleyball/stats/2023#individual', 'Nazareth', 'NazarethCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    scrapeTeamStats('https://gonyuathletics.com/sports/mens-volleyball/stats/2023', 'NYU', 'NYUCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    #not working: scrapeTeamStats('https://stjohnfisher.com/sports/mens-volleyball/stats/2023', 'St John Fisher', 'StJohnFisherCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table')] #change
    scrapeTeamStats('https://nphawks.com/sports/mens-volleyball/stats', 'NewPaltz', 'NewPaltzCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.vassarathletics.com/sports/mens-volleyball/stats/2023', 'Vassar', 'VassarCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.elmira.edu/sports/mens-volleyball/stats/2023', 'Elmira', 'ElmiraCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    
    #MAC
    scrapeTeamStats('https://arcadiaknights.com/sports/mens-volleyball/stats/2023', 'Arcadia', 'ArcadiaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://goeasterneagles.com/sports/mens-volleyball/stats', 'Eastern', 'EasternCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://hoodathletics.com/sports/mens-volleyball/stats', 'Hood', 'HoodCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table' ),
    scrapeTeamStats('https://kingscollegeathletics.com/sports/mens-volleyball/stats', 'Kings', 'KingsCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table' ),
    scrapeTeamStats('https://gomessiah.com/sports/mens-volleyball/stats', 'Messiah', 'MessiahCombineStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.misericordia.edu/sports/mens-volleyball/stats/2022', 'Misericordia', 'MisericordiaCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://stevensducks.com/sports/mens-volleyball/stats/2022', 'Stevens', 'StevensCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gomustangsports.com/sports/mens-volleyball/stats', 'Stevenson', 'StevensonCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://widenerpride.com/sports/mens-volleyball/stats/2023', 'Widener', 'WidenerCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gowilkesu.com/sports/mens-volleyball/stats/2023', 'Wilkes', 'WilkesCombinedStats.csv',  'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table')]


#Concatenate the list of team DataFrames
dfTOTALSTATS = pd.concat(team_dfs, ignore_index=True)
dfTOTALSTATS.to_csv('CombinedStats.csv', index=False)