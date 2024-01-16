import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import datetime

base_url = 'https://ncaa.com'

# Add a custom User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def create_url(year, month, day):
    return f"https://www.ncaa.com/scoreboard/volleyball-men/d3/{year:04d}/{month:02d}/{day:02d}/all-conf"

def fetch_content(url):
    try:
        # Include headers in the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 404:
            return None  # 404 error indicates no games today
        print(f"Error fetching content from {url}: {e}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the scoreboardGames container
    scoreboard_container = soup.find('div', {'id': 'scoreboardGames'})

    # Find all gamePod-link elements within the container
    game_links = scoreboard_container.find_all('a', {'class': 'gamePod-link'})

    return [urljoin(base_url, link['href']) for link in game_links]

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

def html_to_dataframe(html, headers, team_name):
    try:
        # Convert HTML to dataframe
        team_df = pd.read_html(html)[0]
        team_df.columns = headers

        # Exclude the totals row
        team_df = team_df[team_df['Number'] != 'Total']

        # Add a column for the team name
        team_df['Team'] = team_name

        return team_df

    except ValueError:
        print("Error: Unable to create dataframe from HTML.")
        return pd.DataFrame()  # Return an empty DataFrame if parsing fails

if __name__ == "__main__":

    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors')
    
    #change to whatever date to search
    year = 2024
    month = 1
    day = 10
    
    url = create_url(year, month, day)
    html = fetch_content(url)

    if html is not None:
        unique_links = parse_html(html)

        if not unique_links:
            print("No games today.")
        else:
            # Create an empty list to store DataFrames for all games
            all_game_dfs = []

            for game_link in unique_links:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(game_link)

                try:
                    home_team_header = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.boxscore-team-selector-team.home'))
                    )
                    home_team_header.click()

                    home_team_html = get_team_html(driver, 'boxscore-table_player_home')

                    visitor_team_header = WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.boxscore-team-selector-team.away'))
                    )
                    visitor_team_header.click()

                    visitor_team_html = get_team_html(driver, 'boxscore-table_player_visitor')

                    headers = ["Number", "Name", "Sets", "Kills", "Errors", "Total Attempts", "Hit Percentage",
                               "Assists", "Service Aces", "Service Errors", "Reception Errors", "Digs", "Block Solo",
                               "Block Assists", "Block Errors", "Ball Handling Errors", "Points"]

                    home_team_df = html_to_dataframe(home_team_html, headers, 'Home')
                    visitor_team_df = html_to_dataframe(visitor_team_html, headers, 'Visitor')

                    # Check if DataFrames are not empty before concatenating
                    if not home_team_df.empty and not visitor_team_df.empty:
                        combined_df = pd.concat([home_team_df, visitor_team_df], ignore_index=True)
                        all_game_dfs.append(combined_df)

                except Exception as e:
                    print(f"Error processing game: {e}")
                finally:
                    driver.quit()

            if all_game_dfs:
                # Concatenate all DataFrames in the list
                all_games_combined_df = pd.concat(all_game_dfs, keys=range(1, len(all_game_dfs) + 1))

                # Save combined DataFrame to a CSV file
                csv_filename = f"daily_stats_{year}_{month:02d}_{day:02d}.csv"
                all_games_combined_df.to_csv(csv_filename, index=False)

                print(f"Combined dataframe saved to {csv_filename}.")
            else:
                print("No valid games found.")
    else:
        print("No games today or unable to fetch HTML content.")


