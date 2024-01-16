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
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'stats-box'))
        WebDriverWait(driver, 15).until(element_present)
    except Exception as e:
        print(f"Error waiting for stats-box: {e}")
        driver.quit()
        return None

    # Get the HTML content after JavaScript execution
    html = driver.page_source

    # Close the webdriver
    driver.quit()

    return html

def parse_html_with_selenium(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the div with the specified class
    stats_div = soup.find('div', class_='tab-panel active')

    # Find the table within the div
    table = stats_div.find('table')

    # Define headers manually
    headers =  ["Number", 'Name', 'Year', 'Position', 'Matches Played', 'Sets Played', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts', 'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces', 'Service Aces/Set', 'Receptions', 'Reception Errors', 'Digs', 'Digs/Set', 'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set', 'Points', 'Points/Set']

    # Extract data rows, skipping the first row
    data = []
    for row in table.find_all('tr')[1:]:
        # Extract the row data
        row_data = [cell.text.strip() for cell in row.find_all(['td', 'th'])]
        data.append(row_data)

    return headers, data

def parse_and_concat_teams(team_urls, team_names):
    # Initialize an empty DataFrame
    final_df = pd.DataFrame()

    for url, team_name in zip(team_urls, team_names):
        html = fetch_html_with_selenium(url)

        if html:
            headers, data = parse_html_with_selenium(html)

            # Create a DataFrame
            df = pd.DataFrame(data, columns=headers)

            # Drop 'Yr' and 'Pos' columns
            df = df.drop(['Year', 'Position'], axis=1, errors='ignore')
            # Remove '\n' from the 'Name' column
            df['Name'] = df['Name'].apply(lambda x: ' '.join(x.split()))

            # Add 'Team' column based on the manual team name
            df['Team'] = team_name

            # Filter out totals rows
            df = df[df['Number'].ne('')]

            # Concatenate the current team's DataFrame to the final DataFrame
            final_df = pd.concat([final_df, df], ignore_index=True)

    return final_df

if __name__ == "__main__":
    # Define URLs for multiple teams
    team_urls = [
        'https://www.trinethunder.com/sports/mvball/2023-24/teams/trine?view=lineup&r=0&pos=', 
        ]
    

    #Team names dont match with bc of comments out
    # Define manual team names corresponding to the URLs 
    team_names = ['Trine']

    # Parse and concatenate data for multiple teams
    result_df = parse_and_concat_teams(team_urls, team_names)

    # Define the desired order of columns
    desired_order = ['Team', 'Name', 'Number', 'Sets Played', 'Matches Played', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts', 'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces', 'Service Aces/Set', 'Digs', 'Digs/Set', 'Receptions', 'Reception Errors', 'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set', 'Points', 'Points/Set']
    # Reorder the DataFrame columns
    result_df_reordered = result_df[desired_order]

    # Save the final DataFrame to a CSV file
    result_df_reordered.to_csv('CombinedStatsGroupAV3.csv', index=False)

    