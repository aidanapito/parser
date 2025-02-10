import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re

# Define standard headers
STANDARD_HEADERS = [
    'Team', 'Name', 'Number', 'Sets Played', 'Matches Played', 'Kills', 'Kills/Set',
    'Errors', 'Total Attempts', 'Hitting Percentage', 'Assists', 'Assists/Set',
    'Service Aces', 'Service Aces/Set', 'Digs', 'Digs/Set', 'Receptions', 'Reception Errors',
    'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set', 'Points', 'Points/Set'
]

COLUMN_MAPPINGS = {
    "#": "Number", "Name": "Name", "Yr": "Year", "Pos": "Position",
    "gp": "Matches Played", "sp": "Sets Played", "k": "Kills", "k/s": "Kills/Set",
    "e": "Errors", "ta": "Total Attempts", "pct": "Hitting Percentage",
    "a": "Assists", "a/s": "Assists/Set", "sa": "Service Aces", "sa/s": "Service Aces/Set",
    "r": "Receptions", "re": "Reception Errors", "digs": "Digs", "d/s": "Digs/Set",
    "bs": "Block Solo", "ba": "Block Assist", "tot": "Total Blocks", "b/s": "Blocks/Set",
    "pts": "Points", "pts/s": "Points/Set"
}

def fetch_html_with_selenium(driver, url):
    """Fetch page source after waiting for the stats table to load."""
    driver.get(url)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.tabbed-ajax-content[data-url]'))
        )
    except Exception as e:
        print(f"Error loading {url}: {e}")
        return None
    return driver.page_source  # Return page source

def clean_text(text):
    """Clean text by removing extra spaces, newlines, and normalizing empty values."""
    text = text.strip()  # Remove leading/trailing spaces
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text if text not in ['-', ''] else None  # Convert '-' to None

def parse_html_with_bs(html, team_name):
    """Parse the stats tables from the HTML content and standardize column names."""
    soup = BeautifulSoup(html, 'html.parser')

    # Find the div that contains the relevant data
    stats_div = soup.select_one('.tabbed-ajax-content[data-url]')
    if not stats_div:
        print(f"No valid tabbed-ajax-content found for {team_name}")
        return pd.DataFrame()

    # Find the table inside it
    table = stats_div.find('table')
    if not table:
        print(f"No table found in {team_name}")
        return pd.DataFrame()

    # Extract column headers and standardize them
    headers = [clean_text(th.text) for th in table.find_all('th')]
    headers = [COLUMN_MAPPINGS.get(h, h) for h in headers]  # Rename headers based on mapping

    # Extract data rows
    data = []
    for row in table.find('tbody').find_all('tr'):  # Skip header row
        cells = row.find_all('td')
        row_data = [clean_text(cell.text) for cell in cells]

        # Ensure row has the same number of columns as the headers
        row_data += [None] * (len(headers) - len(row_data))  # Fill missing columns
        
        data.append(row_data)

    # Convert to DataFrame
    df = pd.DataFrame(data, columns=headers)
    df['Team'] = team_name  # Add team column

    # Ensure DataFrame has all standard columns
    for col in STANDARD_HEADERS:
        if col not in df.columns:
            df[col] = None  # Add missing columns as empty values

    # Reorder columns to match the required format
    df = df[STANDARD_HEADERS]

    return df

def extract_tables(team_urls, team_names, output_csv='CombinedStatsGroupC2025.csv'):
    """Scrape and combine stats from multiple teams using a single WebDriver session."""
    all_dataframes = []
    
    # Start WebDriver
    driver = webdriver.Chrome()

    for url, team_name in zip(team_urls, team_names):
        print(f"Scraping stats for {team_name}...")
        html = fetch_html_with_selenium(driver, url)
        if html:
            df = parse_html_with_bs(html, team_name)
            if not df.empty:
                all_dataframes.append(df)

    # Close WebDriver
    driver.quit()

    # Combine all teams into one DataFrame
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        combined_df.to_csv(output_csv, index=False)
        print(f"Scraping complete! Data saved to {output_csv}")
    else:
        print("No data was extracted.")

if __name__ == "__main__":
    team_urls = [
        'https://athletics.greenville.edu/sports/mvball/2024-25/teams/greenville?view=lineup',
        'https://www.psblions.com/sports/mvball/2024-25/teams/pennstbehrend?view=lineup',
        'https://athletics.carlow.edu/sports/mvball/2024-25/teams/carlow?view=lineup',
        'https://www.wentworthathletics.com/sports/mvball/2024-25/teams/wentworth?view=lineup',
    ]

    team_names = ['Greenville', 'Behrend', 'Carlow', 'Wentworth']

    extract_tables(team_urls, team_names)





