"""
Roster scraper for 2026 mens volleyball - uses Selenium for JS-rendered pages.
Extracts: name, school, position, class, town, highschool, major, height
Continues on team failures without stopping.
"""

import re
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

# Roster URLs - load from this file or use ROSTER_URLS below
ROSTER_URLS = """
https://adrianbulldogs.com/sports/mens-volleyball/roster
https://arcadiaknights.com/sports/mens-volleyball/roster?view=3
https://athletics.augustana.edu/sports/mens-volleyball/roster?view=3
https://athletics.aurora.edu/sports/mens-volleyball/roster?view=3
https://averettcougars.com/sports/mvball/roster?view=3
https://bwyellowjackets.com/sports/mens-volleyball/roster?view=3
https://bardathletics.com/sports/mens-volleyball/roster
https://athletics.baruch.cuny.edu/sports/mens-volleyball/roster?view=3
https://benueagles.com/sports/mens-volleyball/roster?view=3
https://bethanybison.com/sports/mens-volleyball/roster?view=3
https://bridgewatereagles.com/sports/mens-volleyball/roster/2026?view=3
https://www.brooklyncollegeathletics.com/sports/mens-volleyball/roster?view=3
https://brynathynathletics.com/sports/mens-volleyball/roster?view=3
https://buffalostateathletics.com/sports/mens-volleyball/roster
https://www.cairnhighlanders.com/sports/mens-volleyball/roster?view=3
https://clusports.com/sports/mens-volleyball/roster?view=3
https://calvinknights.com/sports/mens-volleyball/roster?view=3
https://athletics.carthage.edu/sports/mens-volleyball/roster?view=3
https://ccnyathletics.com/sports/mens-volleyball/roster?view=3
https://gochathamcougars.com/sports/mens-volleyball/roster?view=3
https://www.cucougars.com/sports/mens-volleyball/roster?view=3
https://cuwfalcons.com/sports/mens-volleyball/roster?view=3
https://deanbulldogs.com/sports/mens-volleyball/roster?view=3
https://dustars.com/sports/mens-volleyball/roster?view=3
https://drewrangers.com/sports/mvball/roster?view=3
https://goeasterneagles.com/sports/mens-volleyball/roster?view=3
https://emuroyals.com/sports/mens-volleyball/roster?view=3
https://edgewoodeagles.com/sports/mens-volleyball/roster?view=3
https://etownbluejays.com/sports/mens-volleyball/roster?view=3
https://athletics.elmira.edu/sports/mens-volleyball/roster?view=3
https://emersonlions.com/sports/mens-volleyball/roster?view=3
https://goecsaints.com/sports/mens-volleyball/roster?view=3
https://franklingrizzlies.com/sports/mens-volleyball/roster?view=3
https://gallaudetbison.com/sports/mens-volleyball/roster?view=3
https://athletics.geneva.edu/sports/mens-volleyball/roster?view=3
https://greenvillepanthers.com/sports/mens-volleyball/roster?view=3
https://athletics.gcc.edu/sports/mens-volleyball/roster?view=3
https://www.hartwickhawks.com/sports/mens-volleyball/roster?view=3
https://hilberthawks.com/sports/mens-volleyball/roster?view=3
https://hiramterriers.com/sports/mvball/roster?view=3
https://hwsathletics.com/sports/hobart-volleyball/roster
https://hoodathletics.com/sports/mens-volleyball/roster?view=3
https://athletics.houghton.edu/sports/mens-volleyball/roster?view=3
https://www.huntercollegeathletics.com/sports/mens-volleyball/roster?view=3
https://illinoistechathletics.com/sports/mens-volleyball/roster?view=3
https://www.iwusports.com/sports/mens-volleyball/roster?view=3
https://gomightymacs.com/sports/mens-volleyball/roster?view=3
https://johnjayathletics.com/sports/mens-volleyball/roster?view=3
https://keanathletics.com/sports/mens-volleyball/roster?view=3
https://kingscollegeathletics.com/sports/mens-volleyball/roster?view=3
https://lakelandmuskies.com/sports/mens-volleyball/roster?view=3
https://lbcchargers.com/sports/mens-volleyball/roster?view=3
https://lehmanathletics.com/sports/mens-volleyball/roster?view=3
https://duhawks.com/sports/mens-volleyball/roster?view=3
https://lynchburgsports.com/sports/mens-volleyball/roster?view=3
https://govaliants.com/sports/mens-volleyball/roster?view=3
https://mbusabercats.com/sports/mens-volleyball/roster
https://sabreathletics.com/sports/mens-volleyball/roster?view=3
https://marymountsaints.com/sports/mens-volleyball/roster?view=3
https://mecathletics.com/sports/mens-volleyball/roster?view=3
https://gomessiah.com/sports/mens-volleyball/roster?view=3
https://athletics.misericordia.edu/sports/mens-volleyball/roster?view=3
https://mitathletics.com/sports/mens-volleyball/roster?view=3
https://mountieathletics.com/sports/mens-volleyball/roster?view=3
https://msjlions.com/sports/mens-volleyball/roster?view=3
https://athletics.mountunion.edu/sports/mens-volleyball/roster?view=3
https://msoeraiders.com/sports/mens-volleyball/roster?view=3
https://nazathletics.com/sports/mens-volleyball/roster?view=3
https://www.neumannathletics.com/sports/mens-volleyball/roster?view=3
https://nicholsathletics.com/sports/mens-volleyball/roster?view=3
https://njcugothicknights.com/sports/mens-volleyball/roster
https://northcentralcardinals.com/sports/mens-volleyball/roster?view=3
https://athletics.northpark.edu/sports/mens-volleyball/roster?view=3
https://gonyuathletics.com/sports/mens-volleyball/roster?view=3
https://goprattgo.com/sports/mens-volleyball/roster?view=3
https://ramapoathletics.com/sports/mens-volleyball/roster?view=3
https://randolphwildcats.com/sports/mens-volleyball/roster?view=3
https://rmcathletics.com/sports/mens-volleyball/roster?view=3
https://regentroyals.com/sports/mens-volleyball/roster
https://rivierathletics.com/sports/mens-volleyball/roster?view=3
https://roanokemaroons.com/sports/mens-volleyball/roster?view=3
https://rockfordregents.com/sports/mens-volleyball/roster?view=3
https://rutgersnewarkathletics.com/sports/mens-volleyball/roster?view=3
https://seueagles.com/sports/mens-volleyball/roster?view=3
https://athletics.stvincent.edu/sports/mens-volleyball/roster?view=3
https://gogryphons.com/sports/mens-volleyball/roster?view=3
https://suhornets.com/sports/mens-volleyball/roster
https://knightathletics.com/sports/mens-volleyball/roster?view=3
https://spaldingathletics.com/sports/mens-volleyball/roster/2026?view=3
https://springfieldcollegepride.com/sports/mens-volleyball/roster?view=3
https://sjfathletics.com/sports/mens-volleyball/roster?view=3
https://sjbkathletics.com/sports/mens-volleyball/roster?view=3
https://sjliathletics.com/sports/mens-volleyball/roster?view=3
https://athletics.snc.edu/sports/mens-volleyball/roster?view=3
https://stevensducks.com/sports/mens-volleyball/roster?view=3
https://gomustangsports.com/sports/mens-volleyball/roster?view=3
https://nphawks.com/sports/mens-volleyball/roster?view=3
https://www.oldwestburypanthers.com/sports/mens-volleyball/roster?view=3
https://wildcats.sunypoly.edu/sports/mens-volleyball/roster?view=3
https://potsdambears.com/sports/mens-volleyball/roster?view=3
https://www.purchasecollegeathletics.com/sports/mens-volleyball/roster?view=3
https://thielathletics.com/sports/mens-volleyball/roster?view=3
https://trinethunder.com/sports/mens-volleyball/roster?view=3
https://umsvathletics.com/sports/mens-volleyball/roster
https://athletics.uwsp.edu/sports/mens-volleyball/roster?view=3
https://uvfpatriots.com/sports/mvb/roster?view=3
https://www.vassarathletics.com/sports/mens-volleyball/roster?view=3
https://vwuathletics.com/sports/mens-volleyball/roster
https://sports.wabash.edu/sports/mens-volleyball/roster?view=3
https://warrenwilsonowls.com/sports/mens-volleyball/roster?view=3
https://wcbluejays.wcmo.edu/sports/mens-volleyball/roster?view=3
https://wheatoncollegelyons.com/sports/mens-volleyball/roster/2026?view=3
https://widenerpride.com/sports/mens-volleyball/roster?view=3
https://gowilkesu.com/sports/mens-volleyball/roster?view=3
https://wilsonphoenix.com/sports/mens-volleyball/roster?view=3
https://wlcsports.com/sports/mens-volleyball/roster?view=3
https://yumacs.com/sports/mens-volleyball/roster?view=3
https://yorkathletics.com/sports/mens-volleyball/roster?view=3
"""

COLUMNS = ['name', 'school', 'position', 'class', 'town', 'highschool', 'major', 'height']


def url_to_school(url: str) -> str:
    """Derive school name from roster URL domain."""
    parsed = urlparse(url)
    host = (parsed.netloc or url).lower()
    # Remove www.
    if host.startswith('www.'):
        host = host[4:]
    # athletics.X.edu -> X, www.X.com -> X
    if host.startswith('athletics.'):
        host = host.split('.', 1)[1]
    # Get the main subdomain/domain before .edu/.com
    parts = host.replace('.edu', '').replace('.com', '').split('.')
    # e.g. baruch.cuny -> baruch, stevensducks -> stevensducks
    main = parts[0] if parts else host
    # Clean common suffixes
    for suffix in ('athletics', 'sports', 'college', 'go', 'goc'):
        if main.endswith(suffix) and len(main) > len(suffix):
            main = main
        elif main == suffix and len(parts) > 1:
            main = parts[1]
    return main.replace('-', ' ').title()


def _text(el, default=''):
    if el is None:
        return default
    return (el.get_text() or '').strip().replace('\n', ' ').replace('\r', ' ')


def _parse_sidearm_cards(soup: BeautifulSoup, school: str) -> list[dict]:
    """Parse Sidearm card layout: #sidearm-m-roster or .sidearm-roster-players-container + .sidearm-list-card-item"""
    roster_data = []
    containers = [
        soup.select('#sidearm-m-roster .sidearm-list-card-item'),
        soup.select('#sidearm-w-roster .sidearm-list-card-item'),
        soup.select('.sidearm-roster-players-container .sidearm-list-card-item'),
        soup.select('.sidearm-roster-players-container .sidearm-roster-player'),
        soup.select('.sidearm-roster-player'),
    ]
    items = []
    for sel in containers:
        if sel:
            items = sel
            break

    for item in items:
        if 'coach' in _text(item).lower()[:100] or 'staff' in _text(item).lower()[:100]:
            continue
        try:
            # Name: first + last or single name field
            first = item.select_one('.sidearm-roster-player-first-name')
            last = item.select_one('.sidearm-roster-player-last-name')
            if first or last:
                name = f"{_text(first)} {_text(last)}".strip()
            else:
                name_el = item.select_one('.sidearm-roster-player-name h3 a') or item.select_one('.sidearm-roster-player-name a') or item.select_one('h3 a')
                name = _text(name_el)
            if not name:
                continue
            pos_el = item.select_one('.sidearm-roster-player-position-short') or item.select_one('.sidearm-roster-player-position')
            position = _text(pos_el)
            if len(position) > 10 or '\t' in position:  # Long text or tabs - take short code like OH, MH
                match = re.search(r'\b([A-Z]{2,4}(?:\s*/\s*[A-Z]{2,4})*)\b', position)
                position = match.group(1) if match else position[:20]
            acad_year = _text(item.select_one('.sidearm-roster-player-academic-year'))
            town = _text(item.select_one('.sidearm-roster-player-hometown'))
            highschool = _text(item.select_one('.sidearm-roster-player-highschool'))
            height = _text(item.select_one('.sidearm-roster-player-height'))
            # Major: sidearm-roster-player-major, custom1/custom2, or extract from academic-year if combined
            major = _text(item.select_one('.sidearm-roster-player-major') or item.select_one('.sidearm-roster-player-custom1') or item.select_one('.sidearm-roster-player-custom2'))
            if not major and acad_year:
                for prefix in ('Jr.', 'Sr.', 'So.', 'Fr.', 'Fy.', 'Gr.', 'Junior', 'Senior', 'Sophomore', 'Freshman', 'First-Year', 'Graduate'):
                    if acad_year.startswith(prefix):
                        rest = acad_year[len(prefix):].strip()
                        if rest and len(rest) > 2 and rest[0].isalpha():
                            major = rest
                            acad_year = prefix  # keep only class for class field
                        break
            roster_data.append({
                'name': name, 'school': school, 'position': position,
                'class': acad_year, 'town': town, 'highschool': highschool,
                'major': major, 'height': height
            })
        except Exception:
            continue
    return roster_data


def _parse_sidearm_table(soup: BeautifulSoup, school: str) -> list[dict]:
    """Parse roster table (common on Sidearm view=2 or embedded table)."""
    roster_data = []
    table = soup.select_one('table.rotatable_table tbody') or soup.select_one('table tbody')
    if not table:
        return []
    rows = table.select('tr')
    col_map = {}  # idx -> field name
    for row in rows:
        cells = row.find_all(['td', 'th'])
        if not cells:
            continue
        first_text = (cells[0].get_text() or '').strip().lower()
        if 'name' in first_text or first_text in ('#', 'no', 'no.', ''):
            headers = [c.get_text(strip=True).lower() for c in cells]
            for i, h in enumerate(headers):
                if 'pos' in h or h == 'pos.':
                    col_map['pos'] = i
                elif 'cl' in h or 'class' in h:
                    col_map['class'] = i
                elif 'ht' in h or 'height' in h:
                    col_map['ht'] = i
                elif 'hometown' in h or 'high school' in h:
                    col_map['town_hs'] = i
                elif 'major' in h:
                    col_map['major'] = i
            continue
        if not row.find_all('td'):
            continue
        name_el = row.select_one('a[href*="/roster/"]')
        if not name_el:
            continue
        name = _text(name_el)
        if not name or len(name) < 3 or any(x in name.lower() for x in ['coach', 'coordinator', 'director']):
            continue
        texts = [c.get_text(strip=True) for c in cells]
        pos = texts[col_map['pos']] if 'pos' in col_map and col_map['pos'] < len(texts) else ''
        cl = texts[col_map['class']] if 'class' in col_map and col_map['class'] < len(texts) else ''
        ht = texts[col_map['ht']] if 'ht' in col_map and col_map['ht'] < len(texts) else ''
        town, hs = '', ''
        if 'town_hs' in col_map and col_map['town_hs'] < len(texts):
            parts = texts[col_map['town_hs']].split('/', 1)
            town = parts[0].strip()
            hs = parts[1].strip() if len(parts) > 1 else ''
        major = texts[col_map['major']] if 'major' in col_map and col_map['major'] < len(texts) else ''
        # Fallback: pattern match if no header found
        if not col_map:
            for t in texts:
                if not cl and re.match(r'^(Fr|So|Jr|Sr|Fy|Gr)\.?$', t, re.I):
                    cl = t
                elif not ht and re.match(r'^\d-\d+$|^\d\'\d+"', t):
                    ht = t
                elif not pos and re.match(r'^[A-Z]{2,4}(/[A-Z\s/]+)*$', t):
                    pos = t
                elif not town and '/' in t and len(t) > 6:
                    parts = t.split('/', 1)
                    town, hs = parts[0].strip(), (parts[1].strip() if len(parts) > 1 else '')
                elif not major and len(t) > 5 and not re.match(r'^\d+$', t):
                    major = t
        roster_data.append({
            'name': name, 'school': school, 'position': pos,
            'class': cl, 'town': town, 'highschool': hs,
            'major': major, 'height': ht
        })
    return roster_data


def scrape_roster_url(driver, url: str) -> list[dict]:
    """Scrape a single roster URL. Returns list of player dicts."""
    school = url_to_school(url)
    import time
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'main, .main-content, #main-content, table, .roster, .sidearm-roster, [class*="roster"]'))
        )
    except Exception:
        pass
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    data = _parse_sidearm_cards(soup, school)
    if not data:
        data = _parse_sidearm_table(soup, school)
    return data


def run_scraper(output_csv: str = '2026_roster_cards.csv'):
    urls = [u.strip() for u in ROSTER_URLS.strip().splitlines() if u.strip() and u.strip().startswith('http')]
    all_rows = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    with webdriver.Chrome(options=chrome_options) as driver:
        for i, url in enumerate(urls):
            school = url_to_school(url)
            try:
                rows = scrape_roster_url(driver, url)
                if rows:
                    all_rows.extend(rows)
                    print(f"[{i+1}/{len(urls)}] {school}: {len(rows)} players")
                else:
                    print(f"[{i+1}/{len(urls)}] {school}: no players found (skipping)")
            except Exception as e:
                print(f"[{i+1}/{len(urls)}] {school}: FAILED - {e}")
                continue

    df = pd.DataFrame(all_rows, columns=COLUMNS)
    df.to_csv(output_csv, index=False)
    print(f"\nSaved {len(df)} players to {output_csv}")
    return df


if __name__ == '__main__':
    run_scraper()
