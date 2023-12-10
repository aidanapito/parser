import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

def get_team_html(driver, team_table_class):
    try:
        # Wait for the team table to be present
        team_html_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, team_table_class))
        )

        # Return the HTML of the team's page
        return team_html_element.get_attribute('outerHTML')

    except NoSuchElementException:
        print(f"Error: Could not find {team_table_class} table for the team.")
        return None

def html_to_dataframe(html, headers):
    try:
        # Convert HTML to dataframe
        team_df = pd.read_html(html)[0]
        team_df.columns = headers

        # Exclude the totals row
        team_df = team_df[team_df['Number'] != 'Total']
        return team_df

    except ValueError:
        print("Error: Unable to create dataframe from HTML.")
        return None

if __name__ == "__main__":

    current_date = datetime.now().strftime('%Y-%m-%d')

    main_url = 'https://www.ncaa.com/game/6085043'

    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(main_url)

        # Click on the home team header
        home_team_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.boxscore-team-selector-team.home'))
        )
        home_team_name = home_team_header.text.strip()

        home_team_header.click()

        # Extract home team HTML
        home_team_html = get_team_html(driver, 'boxscore-table_player_home')

        # Click on the visitor team header
        visitor_team_header = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.boxscore-team-selector-team.away'))
        )
        visitor_team_name = visitor_team_header.text.strip()

        visitor_team_header.click()

        # Extract visitor team HTML
        visitor_team_html = get_team_html(driver, 'boxscore-table_player_visitor')

        # Define custom headers
        headers = ["Number", "Name", "Sets", "Kills", "Errors", "Total Attempts", "Hit Percentage",
                   "Assists", "Service Aces", "Service Errors", "Reception Errors", "Digs", "Block Solo",
                   "Block Assists", "Block Errors", "Ball Handling Errors", "Points"]

        # Convert HTML to dataframes
        home_team_df = html_to_dataframe(home_team_html, headers)
        visitor_team_df = html_to_dataframe(visitor_team_html, headers)

        # Combine dataframes
        combined_df = pd.concat([home_team_df, visitor_team_df], keys=[home_team_name, visitor_team_name])

        csv_filename = f"{current_date}_{home_team_name}_vs_{visitor_team_name}_stats.csv"
        combined_df.to_csv(csv_filename, index=False)

        print(f"Combined dataframe saved to {csv_filename}.")

    finally:
        driver.quit()