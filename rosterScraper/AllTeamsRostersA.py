import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def scrapeRosterTable(url, team_name, output_filename, roster_selector):
    page_source = None
    # Try requests first (faster, works for PrestoSports static pages)
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.ok:
            page_source = r.text
    except Exception:
        pass

    # Fall back to Selenium for JS-rendered pages
    if page_source is None:
        try:
            with webdriver.Chrome() as driver:
                driver.get(url)
                try:
                    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, f'{roster_selector}, table')))
                except Exception:
                    pass
                time.sleep(2)
                page_source = driver.page_source
        except Exception as e:
            print(f"Failed to load page for {team_name}: {e}")
            return pd.DataFrame()

    soup = BeautifulSoup(page_source, 'html.parser')
    roster_table = soup.select_one(f'{roster_selector} table tbody') or soup.select_one('table tbody')

    if not roster_table:
        print(f"Roster table not found for {team_name} at {url}")
        return pd.DataFrame()

    roster_data = []
    rows = roster_table.find_all('tr')

    for row in rows:
        try:
            all_cells = row.find_all('td')
            cell_values = [cell.text.strip() for cell in all_cells]
            name_cell = row.find('th', class_='name') or row.find('th')
            player_name = ''
            if name_cell:
                # Prefer aria-label (e.g. "Temmy Argynbay image thumbnail")
                for a in name_cell.find_all('a'):
                    if a.get('aria-label'):
                        player_name = a['aria-label'].split(' image')[0].strip()
                        break
                if not player_name:
                    # Fallback: clean whitespace from text (may have "First Last" repeated)
                    parts = name_cell.get_text().split()
                    if len(parts) >= 2:
                        player_name = f"{parts[0]} {parts[-1]}"  # First + Last
                    else:
                        player_name = ' '.join(parts)
            bio_link = name_cell.find('a')['href'] if name_cell and name_cell.find('a') else ''
            img_el = name_cell.find('img') if name_cell else None
            image_url = (img_el.get('data-src') or img_el.get('src') or '') if img_el else ''

            def strip_prefix(s, prefixes):
                for p in prefixes:
                    if s.startswith(p):
                        return s[len(p):].strip()
                return s

            # PrestoSports format: 8 cols [No, Pos, Cl, Ht, Wt, Hometown/HS, Club, Major] - Name in th
            if len(cell_values) >= 8:
                hometown_raw = strip_prefix(cell_values[5], ['Hometown/High School:', 'Hometown/High School'])
                hometown_raw = hometown_raw.replace('\r', ' ').replace('\n', ' ').strip()
                hometown, high_school = hometown_raw.split('/', 1) if '/' in hometown_raw else (hometown_raw, '')
                roster_data.append([
                    team_name,
                    player_name,
                    cell_values[0],
                    strip_prefix(cell_values[1], ['Pos.:', 'Pos.']),
                    strip_prefix(cell_values[2], ['Cl.:', 'Cl.']),
                    strip_prefix(cell_values[3], ['Ht.:', 'Ht.']),
                    strip_prefix(cell_values[4], ['Wt.:', 'Wt.']),
                    hometown.strip(),
                    high_school.strip(),
                    strip_prefix(cell_values[6], ['Club Team:', 'Club Team']),
                    strip_prefix(cell_values[7], ['Major:', 'Major']),
                    bio_link,
                    image_url
                ])
            # Standard format: 9+ cols [No, Name, Pos, Cl, Ht, Wt, Hometown/HS, Club, Major]
            elif len(cell_values) >= 9:
                hometown, high_school = cell_values[6].split('/', 1) if '/' in cell_values[6] else (cell_values[6], '')
                roster_data.append([
                    team_name,
                    player_name or cell_values[1],
                    cell_values[0],
                    cell_values[2],
                    cell_values[3],
                    cell_values[4],
                    cell_values[5],
                    hometown.strip(),
                    high_school.strip(),
                    cell_values[7],
                    cell_values[8],
                    bio_link,
                    image_url
                ])
        except Exception as e:
            print(f"Error processing row for {team_name}: {e}")
    
    columns = ['Team', 'Player Name', 'Jersey Number', 'Position', 'Academic Year', 'Height', 'Weight', 
               'Hometown', 'High School', 'Club Team', 'Major', 'Bio Link', 'Image URL']
    df_roster = pd.DataFrame(roster_data, columns=columns)
    df_roster.to_csv(output_filename, index=False)
    return df_roster



# PrestoSports sites use ?view=2 for table layout
def roster_url(url):
    return url if '?' in url else f'{url}?view=2'

teams = [
    {'url': roster_url('https://www.wentworthathletics.com/sports/mvball/2025-26/roster'), 'name': 'Wentworth', 'selector': '.roster'},
    {'url': roster_url('https://laserpride.lasell.edu/sports/mvball/2025-26/roster'), 'name': 'Lasell', 'selector': '.roster'},
    {'url': roster_url('https://www.psblions.com/sports/mvball/2025-26/roster'), 'name': 'PennStateBehrend', 'selector': '.roster'},
    {'url': roster_url('https://www.juniatasports.net/sports/mvball/2025-26/roster'), 'name': 'Juniata', 'selector': '.roster'},
    {'url': roster_url('https://www.goregispride.com/sports/mvball/2025-26/roster'), 'name': 'Regis', 'selector': '.roster'},
    {'url': roster_url('https://www.bwyellowjackets.com/sports/mvball/2025-26/roster'), 'name': 'BaldwinWallace', 'selector': '.roster'},
    {'url': roster_url('https://wittenbergtigers.com/sports/mvball/2025-26/roster'), 'name': 'Wittenberg', 'selector': '.roster'},
    {'url': roster_url('https://www.ecgulls.com/sports/mvball/2025-26/roster'), 'name': 'Endicott', 'selector': '.roster'},
    {'url': roster_url('https://nvubadgers.com/sports/mvball/2025-26/roster'), 'name': 'NVUJohnson', 'selector': '.roster'},
    {'url': roster_url('https://www.sagegators.com/sports/mvball/2025-26/roster'), 'name': 'Sage', 'selector': '.roster'},
    {'url': roster_url('https://wildcats.sunypoly.edu/sports/mvball/2025-26/roster'), 'name': 'SUNYPoly', 'selector': '.roster'},
    {'url': roster_url('https://www.bethanybison.com/sports/mvball/2025-26/roster'), 'name': 'Bethany', 'selector': '.roster'},
    {'url': roster_url('https://athletics.carlow.edu/sports/mvball/2025-26/roster'), 'name': 'Carlow', 'selector': '.roster'},
    {'url': roster_url('https://simpsonathletics.com/sports/mvball/2025-26/roster'), 'name': 'Simpson', 'selector': '.roster'},
    {'url': roster_url('https://www.fisherfalcons.com/sports/mvball/2025-26/roster'), 'name': 'Fisher', 'selector': '.roster'},
    {'url': roster_url('https://www.rivierathletics.com/sports/mvball/2025-26/roster'), 'name': 'Rivier', 'selector': '.roster'},
    {'url': roster_url('https://www.psaltoonalions.com/sports/mvball/2025-26/roster'), 'name': 'PennStateAltoona', 'selector': '.roster'},
    {'url': roster_url('https://www.cuwfalcons.com/sports/mvball/2025-26/roster'), 'name': 'ConcordiaWisconsin', 'selector': '.roster'},
    {'url': roster_url('https://athletics.elms.edu/sports/mvball/2025-26/roster'), 'name': 'Elms', 'selector': '.roster'},
    {'url': roster_url('https://www.olivetcomets.com/sports/mvball/2025-26/roster'), 'name': 'Olivet', 'selector': '.roster'},
    {'url': roster_url('https://www.fontbonnegriffins.com/sports/mvball/2025-26/roster'), 'name': 'Fontbonne', 'selector': '.roster'},
    {'url': roster_url('https://www.goecsaints.com/sports/m-volley/2025-26/roster'), 'name': 'EmmanuelMass', 'selector': '.roster'},
    {'url': roster_url('https://athletics.enc.edu/sports/mvball/2025-26/roster'), 'name': 'EasternNazarene', 'selector': '.roster'}
]

#15
# Process each team
all_rosters = []

for team in teams:
    print(f"Scraping roster for {team['name']}...")
    try:
        output_filename = f"{team['name']}_Roster.csv"
        df_team_roster = scrapeRosterTable(url=team['url'], team_name=team['name'], output_filename=output_filename, roster_selector=team['selector'])
        if not df_team_roster.empty:
            all_rosters.append(df_team_roster)
    except Exception as e:
        print(f"Failed to scrape {team['name']}: {e}")

# Combine all team rosters into one DataFrame
if not all_rosters:
    print("No rosters were successfully scraped.")
    df_combined_rosters = pd.DataFrame()
else:
    df_combined_rosters = pd.concat(all_rosters, ignore_index=True)

# Save the combined DataFrame to a CSV file
if not df_combined_rosters.empty:
    df_combined_rosters.to_csv('AllTeamsRosterGroupA.csv', index=False)
    print(f"Saved {len(df_combined_rosters)} players to AllTeamsRosterGroupA.csv")
    print(df_combined_rosters.head())
