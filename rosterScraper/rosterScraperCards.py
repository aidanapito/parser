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
    roster_items = soup.select(f'{roster_selector} .sidearm-list-card-item')

    roster_data = []

    for item in roster_items:
        try:
            # Extract player details
            player_first_name = item.select_one('.sidearm-roster-player-first-name').text.strip() if item.select_one('.sidearm-roster-player-first-name') else ''
            player_last_name = item.select_one('.sidearm-roster-player-last-name').text.strip() if item.select_one('.sidearm-roster-player-last-name') else ''
            player_name = f"{player_first_name} {player_last_name}".strip()

            jersey_number = item.select_one('.sidearm-roster-player-jersey span').text.strip() if item.select_one('.sidearm-roster-player-jersey span') else ''
            height = item.select_one('.sidearm-roster-player-height').text.strip() if item.select_one('.sidearm-roster-player-height') else ''
            weight = item.select_one('.sidearm-roster-player-weight').text.strip() if item.select_one('.sidearm-roster-player-weight') else ''
            position = item.select_one('.sidearm-roster-player-position-short').text.strip() if item.select_one('.sidearm-roster-player-position-short') else ''
            academic_year = item.select_one('.sidearm-roster-player-academic-year').text.strip() if item.select_one('.sidearm-roster-player-academic-year') else ''
            hometown = item.select_one('.sidearm-roster-player-hometown').text.strip() if item.select_one('.sidearm-roster-player-hometown') else ''
            high_school = item.select_one('.sidearm-roster-player-highschool').text.strip() if item.select_one('.sidearm-roster-player-highschool') else ''
            club = item.select_one('.sidearm-roster-player-custom1').text.strip() if item.select_one('.sidearm-roster-player-custom1') else ''
            bio_link = item.select_one('.sidearm-roster-player-bio-link')['href'] if item.select_one('.sidearm-roster-player-bio-link') else ''

            roster_data.append([team_name, player_name, jersey_number, height, weight, position, academic_year, hometown, high_school, club, bio_link])
        except Exception as e:
            print(f"Error processing player: {e}")

    # Define column names
    columns = ['Team', 'Player Name', 'Jersey Number', 'Height', 'Weight', 'Position', 'Academic Year', 'Hometown', 'High School', 'Club', 'Bio Link']
    df_roster = pd.DataFrame(roster_data, columns=columns)

    # Save to CSV
    df_roster.to_csv(output_filename, index=False)
    return df_roster


teams = [
    {'url': 'https://rutgersnewarkathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'RutgersNewark', 'selector': '#sidearm-m-roster'},
    {'url': 'https://knightathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'SouthernVirginia', 'selector': '#sidearm-m-roster'},
    {'url': 'https://keanathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Kean', 'selector': '#sidearm-m-roster'},
    {'url': 'https://marymountsaints.com/sports/mens-volleyball/roster?view=3', 'name': 'Marymount', 'selector': '#sidearm-m-roster'},
    {'url': 'https://rmcathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'RandolphMacon', 'selector': '#sidearm-m-roster'},
    {'url': 'https://roanokemaroons.com/sports/mens-volleyball/roster?view=3', 'name': 'Roanoke', 'selector': '#sidearm-m-roster'},
    {'url': 'https://etownbluejays.com/sports/mens-volleyball/roster?view=3', 'name': 'Elizabethtown', 'selector': '#sidearm-m-roster'},
    {'url': 'dg', 'name': 'EasternMennonite', 'selector': '#sidearm-m-roster'},
    {'url': 'https://gomightymacs.com/sports/mens-volleyball/roster?view=3', 'name': 'Immaculata', 'selector': '#sidearm-m-roster'},
    # UVC
    {'url': 'https://mitathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'MIT', 'selector': '#sidearm-m-roster'},
    {'url': 'https://nazathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Nazareth', 'selector': '#sidearm-m-roster'},
    {'url': 'https://gonyuathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'NYU', 'selector': '#sidearm-m-roster'},
    {'url': 'https://sjfathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'St John Fisher', 'selector': '#sidearm-m-roster'},
    {'url': 'https://nphawks.com/sports/mens-volleyball/roster?view=3', 'name': 'SUNY New Paltz', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.vassarathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Vassar', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.elmira.edu/sports/mens-volleyball/roster?view=3', 'name': 'Elmira', 'selector': '#sidearm-m-roster'},
    # MAC
    {'url': 'https://arcadiaknights.com/sports/mens-volleyball/roster?view=3', 'name': 'Arcadia', 'selector': '#sidearm-m-roster'},
    {'url': 'https://goeasterneagles.com/sports/mens-volleyball/roster?view=3', 'name': 'Eastern', 'selector': '#sidearm-m-roster'},
    {'url': 'https://hoodathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Hood', 'selector': '#sidearm-m-roster'},
    {'url': 'https://kingscollegeathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Kings', 'selector': '#sidearm-m-roster'},
    {'url': 'https://gomessiah.com/sports/mens-volleyball/roster?view=3', 'name': 'Messiah', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.misericordia.edu/sports/mens-volleyball/roster?view=3', 'name': 'Misericordia', 'selector': '#sidearm-m-roster'},
    {'url': 'https://stevensducks.com/sports/mens-volleyball/roster?view=3', 'name': 'Stevens', 'selector': '#sidearm-m-roster'},
    {'url': 'https://gomustangsports.com/sports/mens-volleyball/roster?view=3', 'name': 'Stevenson', 'selector': '#sidearm-m-roster'},
    {'url': 'https://widenerpride.com/sports/mens-volleyball/roster?view=3', 'name': 'Widener', 'selector': '#sidearm-m-roster'},
    {'url': 'https://gowilkesu.com/sports/mens-volleyball/roster?view=3', 'name': 'Wilkes', 'selector': '#sidearm-m-roster'},
    # CUNY
    {'url': 'https://ccnyathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'CCNY', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.baruch.cuny.edu/sports/mens-volleyball/roster?view=3', 'name': 'Baruch', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.brooklyncollegeathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Brooklyn College', 'selector': '#sidearm-m-roster'},
    {'url': 'https://johnjayathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'John Jay', 'selector': '#sidearm-m-roster'},
    {'url': 'https://lehmanathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Lehman', 'selector': '#sidearm-m-roster'},
    # GNAC
    {'url': 'https://deanbulldogs.com/sports/mens-volleyball/roster?view=3', 'name': 'Dean', 'selector': '#sidearm-m-roster'},
    # AMCC
    {'url': 'https://athletics.geneva.edu/sports/mens-volleyball/roster?view=3', 'name': 'Geneva', 'selector': '#sidearm-m-roster'},
    {'url': 'https://hilberthawks.com/sports/mens-volleyball/roster?view=3', 'name': 'Hilbert', 'selector': '#sidearm-m-roster'},
    {'url': 'https://hiramterriers.com/sports/mvball/roster?view=3', 'name': 'Hiram', 'selector': '#sidearm-m-roster'},
    {'url': 'https://mountieathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Mount Aloysius', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.stvincent.edu/sports/mens-volleyball/roster?view=3', 'name': 'St Vincent', 'selector': '#sidearm-m-roster'},
    {'url': 'https://thielathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Thiel', 'selector': '#sidearm-m-roster'},
    # CCIW
    {'url': 'https://athletics.augustana.edu/sports/mens-volleyball/roster?view=3', 'name': 'Augustana', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.carthage.edu/sports/mens-volleyball/roster?view=3', 'name': 'Carthage', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.iwusports.com/sports/mens-volleyball/roster?view=3', 'name': 'Illinois Wesleyan', 'selector': '#sidearm-m-roster'},
    {'url': 'https://duhawks.com/sports/mens-volleyball/roster?view=3', 'name': 'Loras', 'selector': '#sidearm-m-roster'},
    {'url': 'https://northcentralcardinals.com/sports/mens-volleyball/roster?view=3', 'name': 'North Central', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.northpark.edu/sports/mens-volleyball/roster?view=3', 'name': 'North Park', 'selector': '#sidearm-m-roster'},
    {'url': 'https://sports.wabash.edu/sports/mens-volleyball/roster?view=3', 'name': 'Wabash', 'selector': '#sidearm-m-roster'},
    # CSAC
    {'url': 'https://brynathynathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Bryn Athyn', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.cairnhighlanders.com/sports/mens-volleyball/roster?view=3', 'name': 'Cairn', 'selector': '#sidearm-m-roster'},
    {'url': 'https://seueagles.com/sports/mens-volleyball/roster?view=3', 'name': 'St Elizabeth', 'selector': '#sidearm-m-roster'},
    {'url': 'https://uvfpatriots.com/sports/mvb/roster?view=3', 'name': 'Valley Forge', 'selector': '#sidearm-m-roster'},
    {'url': 'https://wilsonphoenix.com/sports/mens-volleyball/roster?view=3', 'name': 'Wilson', 'selector': '#sidearm-m-roster'},
    # Independents
    {'url': 'https://clusports.com/sports/mens-volleyball/roster?view=3', 'name': 'Cal Lutheran', 'selector': '#sidearm-m-roster'},
    {'url': 'https://drewrangers.com/sports/mvball/roster?view=3', 'name': 'Drew', 'selector': '#sidearm-m-roster'},
    {'url': 'https://lbcchargers.com/sports/mens-volleyball/roster?view=3', 'name': 'Lancaster Bible', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.neumannathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Neumann', 'selector': '#sidearm-m-roster'},
    {'url': 'https://goprattgo.com/sports/mens-volleyball/roster?view=3', 'name': 'Pratt', 'selector': '#sidearm-m-roster'},
    {'url': 'https://goslugs.com/sports/mens-volleyball/roster?view=3', 'name': 'UCSC', 'selector': '#sidearm-m-roster'},
    {'url': 'https://springfieldcollegepride.com/sports/mens-volleyball/roster?view=3', 'name': 'Springfield', 'selector': '#sidearm-m-roster'}
    {'url': 'https://athletics.misericordia.edu/sports/mens-volleyball/roster?view=3', 'name': 'Misericordia', 'selector': '#sidearm-m-roster'},
    {'url': 'https://athletics.baruch.cuny.edu/sports/mens-volleyball/roster?view=3', 'name': 'Baruch', 'selector': '#sidearm-m-roster'},
    {'url': 'https://mountieathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Mount Aloysius', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.cairnhighlanders.com/sports/mens-volleyball/roster?view=3', 'name': 'Cairn', 'selector': '#sidearm-m-roster'},
    {'url': 'https://seueagles.com/sports/mens-volleyball/roster?view=3', 'name': 'St Elizabeth', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.iwusports.com/sports/mens-volleyball/roster?view=3', 'name': 'Illinois Wesleyan', 'selector':  '#sidearm-m-roster'},
    {'url': 'https://drewrangers.com/sports/mvball/roster?view=3', 'name': 'Drew', 'selector': '#sidearm-m-roster'},
    {'url': 'https://www.neumannathletics.com/sports/mens-volleyball/roster?view=3', 'name': 'Neumann', 'selector': '#sidearm-m-roster'},
    {'url': 'https://goslugs.com/sports/mens-volleyball/roster?view=3', 'name': 'UCSC', 'selector': '#sidearm-m-roster'},

]



#50


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
df_combined_rosters.to_csv('AllTeamsRosterCards.csv', index=False)

# Display the combined DataFrame
print(df_combined_rosters.head())