import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def fetch_html_with_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait for the specific div to be present
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'tab-pane.active'))
        WebDriverWait(driver, 15).until(element_present)
    except Exception as e:
        driver.quit()
        return None

    # Get the HTML content after JavaScript execution
    html = driver.page_source

    # Close the webdriver
    driver.quit()

    return html

def parse_html_with_bs(html, team_name):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the div with the specified class
    stats_div = soup.find('div', class_='tab-pane active')

    # Find all tables within the div
    tables = stats_div.find_all('table')[:3]  # Select only the first three tables

    # Create a list to store DataFrames
    dataframes = []

    # Extract data for each table
    for i, table in enumerate(tables):
        # Extract data rows for each table, skipping the first row
        data = []
        for row in table.find_all('tr')[1:]:
            # Extract the row data
            row_data = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
            data.append(row_data)

        # Create a DataFrame for each table with manually named headers
        if i == 0:
            offenseheaders_table1 = ['Number', 'Name', 'Year', 'Position', 'Matches Played', 'Sets Played', 'Kills',
                                     'Kills/Set', 'Errors', 'Total Attempts', 'Hitting Percentage', 'Assists', 'Assists/Set', 'Pts',
                                     'Pts/Set']
            table_df = pd.DataFrame(data, columns=offenseheaders_table1)
        elif i == 1:
            defenseheaders_table2 = ['Number', 'Name', 'Year', 'Position', 'Matches Played', 'Sets Played', 'Digs',
                                     'Digs/Set', 'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set']
            table_df = pd.DataFrame(data, columns=defenseheaders_table2)
        elif i == 2:
            serveReceiveheaders_table3 = ['Number', 'Name', 'Year', 'Position', 'Matches Played', 'Sets Played',
                                          'Service Aces', 'Service Aces/Set', 'Receptions', 'Reception Errors']
            table_df = pd.DataFrame(data, columns=serveReceiveheaders_table3)

        # Process the 'Name' column to remove extra white spaces
        table_df['Name'] = table_df['Name'].str.replace(r'\s+', ' ', regex=True)


        # Drop specific columns from DataFrames 2 and 3
        if i == 0:
            columns_to_drop = ['Year', 'Position', 'Pts', 'Pts/Set']
            table_df = table_df.drop(columns=columns_to_drop, errors='ignore')
        elif i == 1:  # DataFrame 2
            columns_to_drop = ['Number', 'Name', 'Year', 'Position', 'Matches Played', 'Sets Played'] 
            table_df = table_df.drop(columns=columns_to_drop, errors='ignore')
        elif i == 2:  # DataFrame 3
            columns_to_drop = ['Number', 'Name', 'Year', 'Position', 'Matches Played', 'Sets Played'] 
            table_df = table_df.drop(columns=columns_to_drop, errors='ignore')

        # Reset the index to ensure it's unique
        table_df = table_df.reset_index(drop=True)

        # Add a copy of the DataFrame to the list
        dataframes.append(table_df.copy())

    return dataframes

def extract_tables(team_urls, team_names, output_csv='CombinedStatsGroupD.csv'):
    # Initialize an empty list to store DataFrames
    all_dataframes = []

    for url, team_name in zip(team_urls, team_names):
        html = fetch_html_with_selenium(url)

        if html:
            dataframes = parse_html_with_bs(html, team_name)

            # Concatenate all DataFrames for each team and append it to the list
            team_df = pd.concat(dataframes, axis=1) 
            team_df['Team'] = team_name  # Add 'Team' column based on the manual team name

            all_dataframes.append(team_df)

    # Concatenate all DataFrames at the end
    combined_df = pd.concat(all_dataframes, ignore_index=True)

    # Reorder columns based on the desired order
    final_order = [
        'Team', 'Name', 'Number', 'Sets Played', 'Matches Played', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts',
        'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces', 'Service Aces/Set', 'Digs', 'Digs/Set', 'Receptions', 'Reception Errors', 'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set',
    ]

    # Reorder the DataFrame
    combined_df = combined_df[final_order]

    # Save the combined DataFrame to a CSV file
    combined_df.to_csv(output_csv, index=False)

if __name__ == "__main__":
    # Define URLs for multiple teams
    team_urls = [
        'https://www.olivetcomets.com/sports/mvball/2022-23/teams/olivet?view=lineup&r=0&pos=', 
        'https://www.fontbonnegriffins.com/sports/mvball/2022-23/teams/fontbonne?view=lineup&r=0&pos=',
        'https://www.goecsaints.com/sports/m-volley/2022-23/teams/emmanuelmass?view=lineup&r=0&pos=',
        'https://athletics.enc.edu/sports/mvball/2022-23/teams/easternnazarene?view=lineup&r=0&pos='
    ]

    # Define manual team names corresponding to the URLs 
    team_names = ['Olivet', 'Fontbonne', 'Emmanuel Mass', 'Eastern Nazarene']

    # Extract and print DataFrames
    extract_tables(team_urls, team_names)
