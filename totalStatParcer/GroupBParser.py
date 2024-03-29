from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrapeTeamStats(url, team_name, output_filename, offensive_selector, defensive_selector):
    with webdriver.Chrome() as driver:
        driver.get(url)

        # Use an explicit wait for a specific element to be present on the page
        offensive_element = (By.CSS_SELECTOR, offensive_selector)
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located(offensive_element))

        page_source = driver.page_source

    soup = BeautifulSoup(page_source, 'html.parser')
    all_player_rows = soup.select(f'{offensive_selector} tbody tr.odd, {offensive_selector} tbody tr.even, {defensive_selector} tbody tr.odd, {defensive_selector} tbody tr.even')

    player_data_offense_list = []
    player_data_defense_list = []

    for row in all_player_rows:
        full_name = row.select_one('td:nth-of-type(2)').text.strip().split('\n')[0]
        if ', ' in full_name:
            first_name, last_name = full_name.split(', ')
            name = f'{last_name.strip()} {first_name.strip()}'
        else:
            name = full_name.strip()

        jersey_number = row.select_one('td:nth-of-type(1)').text.strip()

        if any('offensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            player_data_offense = [team_name, name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_offense_list.append(player_data_offense)
        elif any('defensive' in parent.attrs.get('id', '') for parent in row.find_parents('section')):
            player_data_defense = [name, jersey_number] + [column.text.strip() for column in row.find_all('td')[2:]]
            player_data_defense_list.append(player_data_defense)

    offense_columns = ['Team', 'Name', 'Number', 'Sets Played', 'Matches Played', 'Matches Started',
                        'Points', 'Points/Set', 'Kills', 'Kills/Set', 'Errors', 'Total Attempts',
                        'Hitting Percentage', 'Assists', 'Assists/Set', 'Service Aces',
                        'Service Aces/Set', 'Service Errors', 'ViewBio']
    defense_columns = ['Name', 'Number', 'Sets Played', 'Digs', 'Digs/Set',
                        'Receptions', 'Reception Errors', 'Reception Percentage', 'Reception Errors/Set',
                        'Block Solo', 'Block Assist', 'Total Blocks', 'Blocks/Set', 'Block Errors',
                        'BHE', 'ViewBio']

    df_offense = pd.DataFrame(player_data_offense_list, columns=offense_columns)
    df_defense = pd.DataFrame(player_data_defense_list, columns=defense_columns)

    # Drop unnecessary columns
    df_offense = df_offense.drop(["Matches Started", "Points", "Points/Set", "Service Errors","ViewBio"], axis=1)
    df_defense = df_defense.drop(["Name", "Number", "Sets Played", "Reception Percentage",  "Reception Errors/Set", "Block Errors", "BHE", "ViewBio", ], axis=1)

    df_offense['Team'] = team_name

    # Concatenate the DataFrames
    df_combined_stats = pd.concat([df_offense, df_defense], axis=1)

    return df_combined_stats

# Create a list of team DataFrames
#NEED TO CHANGE ALL URLS WITH 2024 TO 2024!!!!

team_dfs = [ #THESE ARE AL TYPE B 

    #7 minutes to do 26 teams, should take about 30 minutes to run every team hopefully.

    #CVC
    scrapeTeamStats('https://rutgersnewarkathletics.com/sports/mens-volleyball/stats#individual', 'Rutgers Newark', 'RutgersNewarkCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://knightathletics.com/sports/mens-volleyball/stats#individual', 'Southern Virginia', 'SouthernVirginiaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://keanathletics.com/sports/mens-volleyball/stats/2024#individual', 'Kean', 'KeanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://marymountsaints.com/sports/mens-volleyball/stats#individual', 'Marymount', 'MarymountCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table') ,
    scrapeTeamStats('https://rmcathletics.com/sports/mens-volleyball/stats/2024#individual', 'Randolph Macon', 'RandolphMaconCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table') ,#change to 2024 when new season starts
    scrapeTeamStats('https://roanokemaroons.com/sports/mens-volleyball/stats#individual', 'Roanoke', 'RoanokeCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), 
    scrapeTeamStats('https://etownbluejays.com/sports/mens-volleyball/stats/2024#individual', 'Elizabethtown', 'ElizabethtownCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    scrapeTeamStats('https://emuroyals.com/sports/mens-volleyball/stats/2024#individual', 'Eastern Mennonite', 'EasternMennoniteCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #TEST IF NOT B
    scrapeTeamStats('https://gomightymacs.com/sports/mens-volleyball/stats#individual', 'Immaculata', 'ImmaculataCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    #UVC
    scrapeTeamStats('https://mitathletics.com/sports/mens-volleyball/stats/2024#individual', 'MIT', 'MITCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    scrapeTeamStats('https://nazathletics.com/sports/mens-volleyball/stats/2024#individual', 'Nazareth', 'NazarethCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    scrapeTeamStats('https://gonyuathletics.com/sports/mens-volleyball/stats/2024#individual', 'NYU', 'NYUCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'), #change
    scrapeTeamStats('https://sjfathletics.com/sports/mens-volleyball/stats/2024#individual', 'St John Fisher', 'StJohnFisherCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://nphawks.com/sports/mens-volleyball/stats#individual', 'SUNY New Paltz', 'NewPaltzCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.vassarathletics.com/sports/mens-volleyball/stats/2024#individual', 'Vassar', 'VassarCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.elmira.edu/sports/mens-volleyball/stats/2024#individual', 'Elmira', 'ElmiraCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    
    #MAC
    scrapeTeamStats('https://arcadiaknights.com/sports/mens-volleyball/stats/2024#individual', 'Arcadia', 'ArcadiaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://goeasterneagles.com/sports/mens-volleyball/stats#individual', 'Eastern', 'EasternCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://hoodathletics.com/sports/mens-volleyball/stats#individual', 'Hood', 'HoodCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table' ),
    scrapeTeamStats('https://kingscollegeathletics.com/sports/mens-volleyball/stats#individual', 'Kings', 'KingsCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table' ),
    scrapeTeamStats('https://gomessiah.com/sports/mens-volleyball/stats#individual', 'Messiah', 'MessiahCombineStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.misericordia.edu/sports/mens-volleyball/stats/2024#individual', 'Misericordia', 'MisericordiaCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://stevensducks.com/sports/mens-volleyball/stats/2024#individual', 'Stevens', 'StevensCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gomustangsports.com/sports/mens-volleyball/stats#individual', 'Stevenson', 'StevensonCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://widenerpride.com/sports/mens-volleyball/stats/2024#individual', 'Widener', 'WidenerCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gowilkesu.com/sports/mens-volleyball/stats/2024#individual', 'Wilkes', 'WilkesCombinedStats.csv',  'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #CUNY 
    scrapeTeamStats('https://ccnyathletics.com/sports/mens-volleyball/stats/2024#individual', 'CCNY', 'CCNYCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.baruch.cuny.edu/sports/mens-volleyball/stats/2024#individual', 'Baruch', 'BaruchCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.brooklyncollegeathletics.com/sports/mens-volleyball/stats/2024#individual', 'Brooklyn College', 'BrooklynCollegeCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    #scrapeTeamStats('https://www.huntercollegeathletics.com/sports/mens-volleyball/stats/2024#individual', 'Hunter', 'HunterCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://johnjayathletics.com/sports/mens-volleyball/stats/#individual', 'JohnJay', 'JohnJayCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://lehmanathletics.com/sports/mens-volleyball/stats/2024#individual', 'Lehman', 'LehmanCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    #scrapeTeamStats('https://mecathletics.com/sports/mens-volleyball/stats/2024#individual', 'Medgar Evers', 'MedgarEversCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #GNAC
    #scrapeTeamStats('https://www.colby-sawyerathletics.com/sports/mens-volleyball/stats/2024#individual', 'Colby Sawyer', 'ColbySawyerCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://deanbulldogs.com/sports/mens-volleyball/stats#individual', 'Dean', 'DeanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #AMCC
    scrapeTeamStats('https://athletics.geneva.edu/sports/mens-volleyball/stats/2024#individual', 'Geneva', 'GenevaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://hilberthawks.com/sports/mens-volleyball/stats/2024#individual', 'Hilbert', 'HilbertCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://hiramterriers.com/sports/mvball/stats#individual', 'Hiram', 'HiramCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    #scrapeTeamStats('https://medaillesports.com/sports/mens-volleyball/stats#individual', 'Medaille', 'MedailleCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://mountieathletics.com/sports/mens-volleyball/stats#individual', 'Mount Aloysius', 'MountAloysiusCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.stvincent.edu/sports/mens-volleyball/stats/2024#individual', 'St Vincent', 'StVincentCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://thielathletics.com/sports/mens-volleyball/stats/2024#individual', 'Thiel', 'ThielCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #CCIW
    scrapeTeamStats('https://athletics.augustana.edu/sports/mens-volleyball/stats/2024#individual', 'Augustuna', 'AugustanaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.carthage.edu/sports/mens-volleyball/stats#individual', 'Carthage', 'CarthageCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.iwusports.com/sports/mens-volleyball/stats/2024#individual', 'Illinois Wesleyan', 'IllinoisWesleyanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://duhawks.com/sports/mens-volleyball/stats#individual', 'Loras', 'LorasCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://northcentralcardinals.com/sports/mens-volleyball/stats/2024#individual', 'North Central', 'NorthCentralCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.northpark.edu/sports/mens-volleyball/stats/2024#individual', 'North Park', 'NorthParkCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://sports.wabash.edu/sports/mens-volleyball/stats/2024#individual', 'Wabash', 'WabashCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #CSAC
    scrapeTeamStats('https://brynathynathletics.com/sports/mens-volleyball/stats#individual', 'Bryn Athyn', 'BrynathynCombinedStats.csv','section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.cairnhighlanders.com/sports/mens-volleyball/stats#individual', 'Cairn', 'CairnCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://seueagles.com/sports/mens-volleyball/stats#individual', 'St Elizabeth', 'StElizabethCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://uvfpatriots.com/sports/mvb/stats#individual', 'Valley Forge', 'ValleyForgeCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://wilsonphoenix.com/sports/mens-volleyball/stats#individual', 'Wilson', 'WilsonCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),

    #INDEPENDENTS
    scrapeTeamStats('https://clusports.com/sports/mens-volleyball/stats#individual', 'Cal Lutheran', 'CalLutheranCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://drewrangers.com/sports/mvball/stats#individual', 'Drew', 'DrewCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://lbcchargers.com/sports/mens-volleyball/stats/2024#individual', 'Lancaster Bible', 'LancasterBibleCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.neumannathletics.com/sports/mens-volleyball/stats/2024#individual', 'Neumann', 'NeumannCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://goprattgo.com/sports/mens-volleyball/stats#individual', 'Pratt', 'PrattCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://goslugs.com/sports/mens-volleyball/stats#individual', 'UCSC', 'UCSCCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://springfieldcollegepride.com/sports/mens-volleyball/stats/2024#individual', 'Springfield', 'SpringfieldCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),

    #MCVL
    scrapeTeamStats('https://adrianbulldogs.com/sports/mens-volleyball/stats#individual', 'Adrian', 'AdrianCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://msjlions.com/sports/mens-volleyball/stats#individual', 'Mount St Joseph', 'MountStJosephCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),

    #NEAC
    scrapeTeamStats('https://bardathletics.com/sports/mens-volleyball/stats/2024#individual', 'Bard', 'BardCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://nicholsathletics.com/sports/mens-volleyball/stats/2024#individual', 'Nichols', 'NicholsCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://potsdambears.com/sports/mens-volleyball/stats/2024#individual', 'Suny Potsdam', 'SunyPotsdamCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),

    #NACC
    scrapeTeamStats('https://athletics.aurora.edu/sports/mens-volleyball/stats#individual', 'Aurora', 'AuroraCombinedStats.csv','section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://benueagles.com/sports/mens-volleyball/stats/2024#individual', 'Benedictine', 'BenedictineCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.cucougars.com/sports/mens-volleyball/stats/2024#individual', 'Concordia Chicago', 'ConcordiaChicagoCombinedStats.csv','section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://dustars.com/sports/mens-volleyball/stats#individual', 'Dominican', 'DominicanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://edgewoodcollegeeagles.com/sports/mens-volleyball/stats#individual', 'Edgewood', 'EdgewoodCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://sabreathletics.com/sports/mens-volleyball/stats#individual', 'Marian', 'MarianCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://msoeraiders.com/sports/mens-volleyball/stats#individual', 'MSOE', 'MSOECombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://rockfordregents.com/sports/mens-volleyball/stats#individual', 'Rockford', 'RockfordCombinedStats.csv','section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://wlcsports.com/sports/mens-volleyball/stats#individual', 'Wisconsin Lutheran', 'WisconsinLutheranCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://lakelandmuskies.com/sports/mens-volleyball/stats/2024#individual', 'Lakeland', 'LakelandCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    

    #Skyline
    scrapeTeamStats('https://cmsvathletics.com/sports/mens-volleyball/stats#individual', 'Mount St Vincent', 'MountStVincentCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://njcugothicknights.com/sports/mens-volleyball/stats/2024#individual', 'NJCU', 'NJCUCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://ramapoathletics.com/sports/mvball/stats/2024#individual', 'Ramapo', 'RamapoCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gogryphons.com/sports/mens-volleyball/stats/2024#individual', 'Sarah Lawrence', 'SarahLawrenceCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.oldwestburypanthers.com/sports/mens-volleyball/stats#individual', 'SUNY Old Westbury', 'SUNYOldWestburyCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://www.purchasecollegeathletics.com/sports/mens-volleyball/stats/2024#individual', 'Suny Purchase', 'SunyPurchaseCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://sjliathletics.com/sports/mens-volleyball/stats/2024#individual', 'StJoesLi', 'StJoesLiCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://yumacs.com/sports/mens-volleyball/stats/2024#individual', 'Yeshiva', 'YeshivaCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    
    #added
    scrapeTeamStats('https://hwsathletics.com/sports/hobart-volleyball/stats/2024#individual', 'Hobart', 'HobartCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://illinoistechathletics.com/sports/mens-volleyball/stats/2024#individual', 'IllinoisTech', 'IllinoisTechCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://buffalostateathletics.com/sports/mens-volleyball/stats/2024#individual', 'BuffaloState', 'BuffaloStateCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://adrianbulldogs.com/sports/mens-volleyball/stats/2024#individual', 'Adrian', 'AdrianCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://emersonlions.com/sports/mens-volleyball/stats/2024#individual', 'Emerson', 'EmersonCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.uwsp.edu/sports/mens-volleyball/stats/2024#individual', 'UW-StevensPoint', 'StevensPointCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://vwuathletics.com/sports/mens-volleyball/stats/2024#individual', 'VirginiaWesleyan', 'VirginiaWesleyanCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://thielathletics.com/sports/mens-volleyball/stats/2024#individual', 'Thiel', 'ThielCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://govaliants.com/sports/mens-volleyball/stats/2024#individual', 'Manhattanville', 'ManhattanvilleCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://gochathamcougars.com/sports/mens-volleyball/stats/2024#individual', 'Chatham', 'ChathamCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://calvinknights.com/sports/mens-volleyball/stats/2024#individual', 'Calvin', 'CalvinCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.houghton.edu/sports/mens-volleyball/stats/2024#individual', 'Houghton', 'HoughtonCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://mbusabercats.com/sports/mens-volleyball/stats/2024#individual', 'MaranthanBaptist', 'MaranthanBaptistCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://sjbkathletics.com/sports/mens-volleyball/stats/2024#individual', 'StJosephsBrooklyn', 'StJosephsBrooklynCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://yorkathletics.com/sports/mens-volleyball/stats/2024#individual', 'York', 'YorkCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    #scrapeTeamStats('', '', 'CombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://athletics.mountunion.edu/sports/mens-volleyball/stats#individual', 'Mount Union', 'MountUnionCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table', 'section#individual-overall-defensive table.sidearm-table'),
    scrapeTeamStats('https://averettcougars.com/sports/mens-volleyball/stats/2024#individual', 'Averett', 'AverettCombinedStats.csv', 'section#individual-overall-offensive table.sidearm-table','section#individual-overall-defensive table.sidearm-table'),


    
    ]

# Concatenate the list of team DataFrames
df_combined_stats = pd.concat(team_dfs, ignore_index=True)

# Write the DataFrame to a CSV file with the 'Team' column and without including the index
df_combined_stats.to_csv('CombinedStatsGroupB.csv', index=False)

#MISSING: Medaille, no page: Colby-Sawyer, no page: Hunter, no page: Medgar Evans, no page: