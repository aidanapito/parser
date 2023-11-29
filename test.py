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
        offensive_element = (By.CSS_SELECTOR, offensive_selector)
        WebDriverWait(driver, 15).until(EC.visibility_of_element_located(offensive_element))

        page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    all_player_rows = soup.select(f'{offensive_selector} tbody tr.odd, {offensive_selector} tbody tr.even, {defensive_selector} tbody tr.odd, {defensive_selector} tbody tr.even')

    player_data_offense_list = []
    player_data_defense_list = []

    for row in all_player_rows:
        full_name = row.select_one('td:nth-of-type(2)').text.strip().split('\n')[0]
        if ', ' in full_name:
            first_name, last_name = full_name.split(', ')
            name = f'{first_name.strip()} {last_name.strip()}'
        else:
            name = full_name.strip()

        jersey_number = row.select_one('td:nth-of-type(1)').text.strip()

        if any('offensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            player_data_offense = [team_name, name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_offense_list.append(player_data_offense)
        elif any('defensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            player_data_defense = [name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_defense_list.append(player_data_defense)

    offense_columns = ['Team', 'Name', 'Number', 'Sets Played', 'Matches Played', 'Matches Started',
                        'Points', 'Points/Set', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts',
                        'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces',
                        'Service Aces/Set', 'Service Errors', 'ViewBio']
    defense_columns = ['Name', 'Number', 'Sets Played', 'Digs', 'Digs/Set',
                        'Receptions', 'Reception Errors', 'Reception Percentage', 'Reception Errors/Set',
                        'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set', 'Block Errors',
                        'BHE', 'ViewBio']

    df_offense = pd.DataFrame(player_data_offense_list, columns=offense_columns)
    df_defense = pd.DataFrame(player_data_defense_list, columns=defense_columns)

    # Drop unnecessary columns
    df_offense = df_offense.drop(["Matches Started", "Points", "Points/Set", "Service Errors","ViewBio"], axis=1)
    df_defense = df_defense.drop(["Name", "Number", "Sets Played", "Reception Percentage",  "Reception Errors/Set", "Block Errors", "BHE", "ViewBio", ], axis=1)

    df_offense['Team'] = team_name

    # Concatenate the DataFrames
    df_combined_stats = pd.concat([df_offense, df_defense], axis=1)

    return df_combined_stats

# Create a list of team DataFrames
#NEED TO CHANGE ALL URLS WITH 2023 TO 2024!!!!

team_dfs = [ #THESE ARE AL TYPE B 

    #7 minutes to do 26 teams, should take about 30 minutes to run every team hopefully.

    #CVC
    scrapeTeamStats('https://gomightymacs.com/sports/mens-volleyball/stats#individual', 'Immaculata', 'ImmaculataCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    #UVC
    
    #CUNY 
    #scrapeTeamStats('https://www.brooklyncollegeathletics.com/sports/mens-volleyball/stats/2023', 'Brooklyn College', 'BrooklynCollegeCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #GNAC
    scrapeTeamStats('https://deanbulldogs.com/sports/mens-volleyball/stats#individual', 'Dean', 'DeanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #CSAC
    scrapeTeamStats('https://uvfpatriots.com/sports/mvb/stats#individual', 'Valley Forge', 'ValleyForgeCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #INDEPENDENTS
    scrapeTeamStats('https://clusports.com/sports/mens-volleyball/stats/2023#individual', 'Cal Lutheran', 'CalLutheranCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.neumannathletics.com/sports/mens-volleyball/stats/2022#individual', 'Neumann', 'NeumannCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
   
    #MCVL
    scrapeTeamStats('https://adrianbulldogs.com/sports/mens-volleyball/stats#individual', 'Adrian', 'AdrianCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #NACC
    scrapeTeamStats('https://dustars.com/sports/mens-volleyball/stats#individual', 'Dominican', 'DominicanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    ]

# Concatenate the list of team DataFrames
df_combined_stats = pd.concat(team_dfs, ignore_index=True)

# Write the DataFrame to a CSV file with the 'Team' column and without including the index
df_combined_stats.to_csv('CombinedStatsGroupBTest.csv', index=False)