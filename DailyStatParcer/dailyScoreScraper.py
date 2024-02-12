import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup 
from urllib.parse import urljoin
import numpy as np
import requests

base_url = 'https://ncaa.com'

def create_url(year, month, day):
    return f"https://www.ncaa.com/scoreboard/volleyball-men/d3/{year:04d}/{month:02d}/{day:02d}/all-conf"

def fetch_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

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

    scoreboard_container = soup.find('div', {'id': 'scoreboardGames'})
    game_links = scoreboard_container.find_all('a', {'class': 'gamePod-link'})

    return [urljoin(base_url, link['href']) for link in game_links]


def parse_html_for_scores(html):
    soup = BeautifulSoup(html, 'html.parser')

    linescore_teams_container = soup.find('tbody', {'class': 'linescore-teams'})

    if linescore_teams_container:
        home_away_info = []
        teams = []

        for team_container in soup.find_all('div', {'class': 'gamecenter-game-banner-team'}):
            team_name_long = team_container.find('span', {'class': 'team-name-long'}).get_text(strip=True)
            teams.append(team_name_long)

            if 'away' in team_container['class']:
                home_away_info.append('Away')
            elif 'home' in team_container['class']:
                home_away_info.append('Home')

        # Find all linescore-cell elements within the linescore-teams container
        linescore_cell_elements = linescore_teams_container.find_all('td', {'class': 'linescore-cell'})

        # Extract the text content of each linescore-cell element
        linescore_cell_text = [element.get_text(strip=True) for element in linescore_cell_elements]

        # Determine the number of sets played
        num_sets = len(linescore_cell_text) // 2  # Assuming each set has two scores (team1 and team2)

        # Manually assign headers
        headers = ['Team', 'Home/Away'] + [f'Score Set {i}' for i in range(1, num_sets + 1)] + ['Final Score']

        # Create a list to hold the data for each team
        data = [
            [teams[0], home_away_info[0], ''] + linescore_cell_text[:num_sets],
            [teams[1], home_away_info[1], ''] + linescore_cell_text[num_sets:]
        ]


        # Create DataFrames for each team
        df_team1 = pd.DataFrame([data[0]], columns=headers)
        df_team2 = pd.DataFrame([data[1]], columns=headers)

        result_df = pd.concat([df_team1, df_team2], ignore_index=True, sort=False)

        # Fill NaN values in 'Final Score' column with 0
        result_df['Final Score'].fillna(0, inplace=True)

        return result_df

    print("Stats not available or game not played.")
    return pd.DataFrame()

if __name__ == "__main__":
    chrome_options = Options()
    chrome_options.add_argument('--ignore-certificate-errors') 
    
    year = 2024
    month = 2
    day = 11

    url = create_url(year, month, day)
    html = fetch_content(url)

    if html is not None:
        game_links = parse_html(html)
        all_game_data = []

        for game_link in game_links:
            full_url = game_link
            print(f"Processing game link: {full_url}")

            if full_url:
                driver = webdriver.Chrome(options=chrome_options)
                driver.get(full_url)

                try:
                    df = parse_html_for_scores(driver.page_source)
                    
                    if not df.empty:
                        all_game_data.append(df)
                    else:
                        print("No stats available or game not played for this link.")

                except Exception as e:
                    print(f"Error processing game: {e}")
                finally:
                    driver.quit()

        if all_game_data:
            # Concatenate all DataFrames in the list
            result_df = pd.concat(all_game_data, ignore_index=True)

            # Save the result DataFrame to a CSV file without index and header
            csv_filename = f"DailyGameScores2024.csv"
            result_df.to_csv(csv_filename, index=False)
            print(result_df)

            print(f"Combined set scores saved to {csv_filename}.")
        else:
            print("No valid games found.")
    else:
        print("No games today or unable to fetch HTML content.")