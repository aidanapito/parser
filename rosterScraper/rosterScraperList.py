from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrapeRosterInfo(url, team_name, output_filename, roster_selector):
    with webdriver.Chrome() as driver:
        driver.get(url)

        # Wait for the roster container to load
        roster_element = (By.CSS_SELECTOR, roster_selector)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(roster_element))

        page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    roster_items = soup.select(f'{roster_selector} .sidearm-roster-player')

    roster_data = []

    for item in roster_items:
        try:
            # Extract player details
            player_name = item.select_one('.sidearm-roster-player-name h3 a').text.strip() if item.select_one('.sidearm-roster-player-name h3 a') else ''
            jersey_number = item.select_one('.sidearm-roster-player-jersey-number').text.strip() if item.select_one('.sidearm-roster-player-jersey-number') else ''
            position = ' '.join(item.select_one('.sidearm-roster-player-position').text.split()).strip() if item.select_one('.sidearm-roster-player-position') else ''
            height = item.select_one('.sidearm-roster-player-height').text.strip() if item.select_one('.sidearm-roster-player-height') else ''
            academic_year = item.select_one('.sidearm-roster-player-academic-year').text.strip() if item.select_one('.sidearm-roster-player-academic-year') else ''
            hometown = item.select_one('.sidearm-roster-player-hometown').text.strip() if item.select_one('.sidearm-roster-player-hometown') else ''
            high_school = item.select_one('.sidearm-roster-player-highschool').text.strip() if item.select_one('.sidearm-roster-player-highschool') else ''
            bio_link = item.select_one('a[aria-label*="Full Bio"]')['href'] if item.select_one('a[aria-label*="Full Bio"]') else ''
            image_url = item.select_one('.sidearm-roster-player-image img')['src'] if item.select_one('.sidearm-roster-player-image img') else ''

            # Clean up the data
            position = position.replace('\n', '').replace('\t', '').strip()

            roster_data.append([
                team_name,
                player_name,
                jersey_number,
                position,
                height,
                academic_year,
                hometown,
                high_school,
                bio_link,
                image_url
            ])
        except Exception as e:
            print(f"Error processing player: {e}")

    # Define column names
    columns = ['Team', 'Player Name', 'Jersey Number', 'Position', 'Height', 'Academic Year', 'Hometown', 'High School', 'Bio Link', 'Image URL']
    df_roster = pd.DataFrame(roster_data, columns=columns)

    # Save to CSV
    df_roster.to_csv(output_filename, index=False)
    return df_roster


# Teams to scrape
teams = [
    {'url': 'https://rmcathletics.com/sports/mens-volleyball/roster', 'name': 'RandolphMacon', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://roanokemaroons.com/sports/mens-volleyball/roster', 'name': 'Roanoke', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://etownbluejays.com/sports/mens-volleyball/roster', 'name': 'Elizabethtown', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://gomightymacs.com/sports/mens-volleyball/roster', 'name': 'Immaculata', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://athletics.misericordia.edu/sports/mens-volleyball/roster?view=3', 'name': 'Misericordia', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://athletics.baruch.cuny.edu/sports/mens-volleyball/roster?view=3', 'name': 'Baruch', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://mountieathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Mount Aloysius', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://www.cairnhighlanders.com/sports/mens-volleyball/roster?view=3', 'name': 'Cairn', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://seueagles.com/sports/mens-volleyball/roster?view=3', 'name': 'St Elizabeth', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://www.iwusports.com/sports/mens-volleyball/roster?view=3', 'name': 'Illinois Wesleyan', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://drewrangers.com/sports/mvball/roster?view=3', 'name': 'Drew', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://lbcchargers.com/sports/mens-volleyball/roster?view=3', 'name': 'Lancaster Bible', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://www.neumannathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Neumann', 'selector': '.sidearm-roster-players-container'},
    {'url': 'https://springfieldcollegepride.com/sports/mens-volleyball/roster?view=3', 'name': 'Springfield', 'selector': '.sidearm-roster-players-container'},
]
#6
# Process each team
all_rosters = []

for team in teams:
    print(f"Scraping roster for {team['name']}...")
    output_filename = f"{team['name']}_Roster.csv"
    df_team_roster = scrapeRosterInfo(url=team['url'], team_name=team['name'], output_filename=output_filename, roster_selector=team['selector'])
    all_rosters.append(df_team_roster)

# Combine all team rosters into one DataFrame
df_combined_rosters = pd.concat(all_rosters, ignore_index=True)

# Save the combined DataFrame to a CSV file
df_combined_rosters.to_csv('AllTeamsRosterList.csv', index=False)

# Display the combined DataFrame
print(df_combined_rosters.head())
