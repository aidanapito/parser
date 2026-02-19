"""
Roster scraper for 2026 mens volleyball (PrestoSports list/table layout).
Uses Selenium for JS-rendered pages.
Extracts: name, school, position, class, town, highschool, major, height
Same output format as roster_scraper_cards.py. Continues on team failures.
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

ROSTER_URLS = """
https://athletics.carlow.edu/sports/mvball/2025-26/roster
https://athletics.elms.edu/sports/mvball/2025-26/roster
https://www.ecgulls.com/sports/mvball/2025-26/roster
https://www.juniatasports.net/sports/mvball/2025-26/roster
https://laserpride.lasell.edu/sports/mvball/2025-26/roster
https://nvubadgers.com/sports/mvball/2025-26/roster
https://www.olivetcomets.com/sports/mvball/2025-26/roster
https://www.psaltoonalions.com/sports/mvball/2025-26/roster
https://www.psblions.com/sports/mvball/2025-26/roster
https://www.goregispride.com/sports/mvball/2025-26/roster
https://www.sagegators.com/sports/mvball/2025-26/roster
https://simpsonathletics.com/sports/mvball/2025-26/roster
https://www.wentworthathletics.com/sports/mvball/2025-26/roster
https://wittenbergtigers.com/sports/mvball/2025-26/roster
"""

COLUMNS = ['name', 'school', 'position', 'class', 'town', 'highschool', 'major', 'height']


def url_to_school(url: str) -> str:
    """Derive school name from roster URL domain."""
    parsed = urlparse(url)
    host = (parsed.netloc or url).lower()
    if host.startswith('www.'):
        host = host[4:]
    if host.startswith('athletics.'):
        host = host.split('.', 1)[1]
    parts = host.replace('.edu', '').replace('.com', '').split('.')
    main = parts[0] if parts else host
    return main.replace('-', ' ').title()


def _text(el, default=''):
    if el is None:
        return default
    return (el.get_text() or '').strip().replace('\n', ' ').replace('\r', ' ')


def _strip_prefix(s: str, prefixes: list) -> str:
    for p in prefixes:
        if s.startswith(p):
            return s[len(p):].strip()
    return s.strip()


def _parse_presto_table(soup: BeautifulSoup, school: str) -> list[dict]:
    """Parse PrestoSports table layout (.roster table, or table tbody)."""
    roster_data = []
    table = soup.select_one('.roster table tbody') or soup.select_one('table tbody')
    if not table:
        return []

    rows = table.find_all('tr')
    for row in rows:
        try:
            name_cell = row.find('th', class_='name') or row.find('th', attrs={'data-label': re.compile(r'name', re.I)}) or row.find('th')
            if not name_cell:
                continue
            # Name from aria-label ("Temmy Argynbay: jersey number 1: full bio") or link text
            player_name = ''
            for a in name_cell.find_all('a'):
                if a.get('aria-label'):
                    player_name = a['aria-label'].split(':')[0].strip()
                    if ' image' in player_name:
                        player_name = player_name.split(' image')[0].strip()
                    break
            if not player_name:
                link = name_cell.find('a')
                if link:
                    parts = link.get_text().split()
                    player_name = f"{parts[0]} {parts[-1]}" if len(parts) >= 2 else ' '.join(parts)
            if not player_name or len(player_name) < 2:
                continue
            if any(x in player_name.lower() for x in ['coach', 'coordinator', 'director', 'staff']):
                continue

            tds = row.find_all('td')
            if len(tds) < 4:
                continue

            def cell(i: int, prefixes: list) -> str:
                if i >= len(tds):
                    return ''
                return _strip_prefix(tds[i].get_text(strip=True).replace('\n', ' ').replace('\t', ' '), prefixes)

            # Column layout varies: 8-col [No,Pos,Cl,Ht,Wt,Hometown/HS,Club,Major] or 5-col [No,Pos,Cl,Ht,Hometown/HS]
            pos = cell(1, ['Pos.:', 'Pos.'])
            cl = cell(2, ['Cl.:', 'Cl.'])
            ht = cell(3, ['Ht.:', 'Ht.'])
            town = highschool = major = ''
            # Hometown/HS at index 4 or 5 (5-col vs 8-col)
            hometown_idx = 5 if len(tds) >= 6 else 4
            hometown_raw = cell(hometown_idx, ['Hometown/High School:', 'Hometown/High School'])
            hometown_raw = hometown_raw.replace('\r', ' ').replace('\n', ' ').strip()
            town, highschool = hometown_raw.split('/', 1) if '/' in hometown_raw else (hometown_raw, '')
            town = town.strip()
            highschool = highschool.strip()
            major = cell(7, ['Major:']) if len(tds) > 7 else ''

            # Normalize height (6-5 -> 6'5" if needed for consistency)
            if ht and '-' in ht and '"' not in ht:
                ht = ht.replace('-', "'") + '"'

            roster_data.append({
                'name': player_name,
                'school': school,
                'position': pos,
                'class': cl,
                'town': town,
                'highschool': highschool,
                'major': major,
                'height': ht,
            })
        except Exception:
            continue
    return roster_data


def scrape_roster_url(driver, url: str) -> list[dict]:
    """Scrape a single PrestoSports roster URL. Returns list of player dicts."""
    school = url_to_school(url)
    # PrestoSports uses ?view=2 for table layout
    if '?' not in url:
        url = f'{url}?view=2'

    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.roster, table tbody, table'))
        )
    except Exception:
        pass

    import time
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return _parse_presto_table(soup, school)


def run_scraper(output_csv: str = '2026_roster_list.csv'):
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
