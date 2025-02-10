from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrapeRosterTable(url, team_name, output_filename, roster_selector):
    with webdriver.Chrome() as driver:
        driver.get(url)

        # Wait for the roster table to load
        roster_element = (By.CSS_SELECTOR, roster_selector)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(roster_element))

        page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    roster_table = soup.select_one(f'{roster_selector} table tbody')

    if not roster_table:
        print(f"Roster table not found for {team_name} at {url}")
        return pd.DataFrame()

    roster_data = []
    rows = roster_table.find_all('tr')

    for row in rows:
        try:
            all_cells = row.find_all('td')
            cell_values = [cell.text.strip() for cell in all_cells]
            
            # Ensure there are enough columns for parsing
            if len(cell_values) >= 9:
                bio_link = row.find('th', class_='name').find('a')['href'] if row.find('th', class_='name') else ''
                image_url = row.find('th', class_='name').find('img')['data-src'] if row.find('th', class_='name') else ''
                hometown, high_school = cell_values[6].split('/') if '/' in cell_values[6] else (cell_values[6], '')

                roster_data.append([
                    team_name,
                    cell_values[1],  # Player Name
                    cell_values[0],  # Jersey Number
                    cell_values[2],  # Position
                    cell_values[3],  # Academic Year
                    cell_values[4],  # Height
                    cell_values[5],  # Weight
                    hometown.strip(),
                    high_school.strip(),
                    cell_values[7],  # Club Team
                    cell_values[8],  # Major
                    bio_link,
                    image_url
                ])
        except Exception as e:
            print(f"Error processing row: {e}")
    
    columns = ['Team', 'Player Name', 'Jersey Number', 'Position', 'Academic Year', 'Height', 'Weight', 
               'Hometown', 'High School', 'Club Team', 'Major', 'Bio Link', 'Image URL']
    df_roster = pd.DataFrame(roster_data, columns=columns)
    df_roster.to_csv(output_filename, index=False)
    return df_roster



# Example team for testing
teams = [
    {'url': 'https://www.wentworthathletics.com/sports/mvball/2024-25/roster', 'name': 'Wentworth', 'selector': '.roster'},
    {'url': 'https://laserpride.lasell.edu/sports/mvball/2024-25/roster', 'name': 'Lasell', 'selector': '.roster'},
    #{'url': 'https://www.psblions.com/sports/mvball/2024-25/roster', 'name': 'PennStateBehrend', 'selector': '.roster'},
    {'url': 'https://www.juniatasports.net/sports/mvball/2024-25/roster', 'name': 'Juniata', 'selector': '.roster'},
    {'url': 'https://www.goregispride.com/sports/mvball/2024-25/roster', 'name': 'Regis', 'selector': '.roster'},
    #{'url': 'https://www.bwyellowjackets.com/sports/mvball/2024-25/roster', 'name': 'BaldwinWallace', 'selector': '.roster'},
    {'url': 'https://wittenbergtigers.com/sports/mvball/2024-25/roster', 'name': 'Wittenberg', 'selector': '.roster'},
    #{'url': 'https://www.ecgulls.com/sports/mvball/2024-25/roster', 'name': 'Endicott', 'selector': '.roster'},
    {'url': 'https://nvubadgers.com/sports/mvball/2024-25/roster', 'name': 'NVUJohnson', 'selector': '.roster'},
    {'url': 'https://www.sagegators.com/sports/mvball/2024-25/roster', 'name': 'Sage', 'selector': '.roster'},
    #{'url': 'https://wildcats.sunypoly.edu/sports/mvball/2024-25/roster', 'name': 'SUNYPoly', 'selector': '.roster'},
    #{'url': 'https://www.bethanybison.com/sports/mvball/2024-25/roster', 'name': 'Bethany', 'selector': '.roster'},
    #{'url': 'https://athletics.carlow.edu/sports/mvball/2024-25/roster', 'name': 'Carlow', 'selector': '.roster'},
    #{'url': 'https://simpsonathletics.com/sports/mvball/2024-25/roster', 'name': 'Simpson', 'selector': '.roster'},
    #{'url': 'https://www.fisherfalcons.com/sports/mvball/2024-25/roster', 'name': 'Fisher', 'selector': '.roster'}
    {'url': 'https://wells.prestosports.com/sports/mvball/2024-25/roster', 'name': 'Wells', 'selector': '.roster'},
    {'url': 'https://www.rivierathletics.com/sports/mvball/2024-25/roster', 'name': 'Rivier', 'selector': '.roster'},
    {'url': 'https://www.psaltoonalions.com/sports/mvball/2024-25/roster', 'name': 'PennStateAltoona', 'selector': '.roster'},
    {'url': 'https://www.cuwfalcons.com/sports/mvball/2024-25/roster', 'name': 'ConcordiaWisconsin', 'selector': '.roster'},
    {'url': 'https://athletics.elms.edu/sports/mvball/2024-25/roster', 'name': 'Elms', 'selector': '.roster'},
    {'url': 'https://www.olivetcomets.com/sports/mvball/2024-25/roster', 'name': 'Olivet', 'selector': '.roster'},
    {'url': 'https://www.fontbonnegriffins.com/sports/mvball/2024-25/roster', 'name': 'Fontbonne', 'selector': '.roster'},
    {'url': 'https://www.goecsaints.com/sports/m-volley/2024-25/roster', 'name': 'EmmanuelMass', 'selector': '.roster'},
    {'url': 'https://athletics.enc.edu/sports/mvball/2024-25/roster', 'name': 'EasternNazarene', 'selector': '.roster'}
]


# Process each team
all_rosters = []

for team in teams:
    print(f"Scraping roster for {team['name']}...")
    output_filename = f"{team['name']}_Roster.csv"
    df_team_roster = scrapeRosterTable(url=team['url'], team_name=team['name'], output_filename=output_filename, roster_selector=team['selector'])
    all_rosters.append(df_team_roster)

# Combine all team rosters into one DataFrame
df_combined_rosters = pd.concat(all_rosters, ignore_index=True)

# Save the combined DataFrame to a CSV file
df_combined_rosters.to_csv('AllTeamsRosterGroupA.csv', index=False)

# Display the combined DataFrame
print(df_combined_rosters.head())
