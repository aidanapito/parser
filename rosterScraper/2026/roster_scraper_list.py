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

COLUMNS = ['name', 'number', 'school', 'position', 'class', 'town', 'highschool', 'major', 'height']


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


# Prefixes to strip from cell values (different sites use different labels)
CELL_PREFIXES = {
    'number': ['Number:', 'No.:', 'No.'],
    'position': ['Position:', 'Pos.:', 'Pos.'],
    'class': ['Class:', 'Cl.:', 'Cl.', 'Yr.:', 'Yr.'],
    'height': ['Height:', 'Ht.:', 'Ht.'],
    'town_hs': ['Hometown/High School:', 'Hometown/High School', 'Hometown/Previous School:',
                'Hometown/Previous School', 'Hometown:', 'High School:', 'Hometown / High School:'],
    'major': ['Major:', 'Minor:', 'Major/Minor:'],
}


def _has_redundant_no_column(tds: list) -> bool:
    """Some sites (Psaltoonalions, Simpson) have td[0]=number and td[1]='No.:1' - redundant."""
    if len(tds) < 2:
        return False
    first = (tds[0].get_text() or '').strip()
    second = (tds[1].get_text() or '').strip()
    if not first or not second:
        return False
    # First td is plain number, second starts with No.: / Number:
    if not re.match(r'^\d+$', first):
        return False
    for p in ['No.:', 'No.', 'Number:', 'Number']:
        if second.startswith(p):
            return True
    return False


def _map_headers_to_indices(header_texts: list[str], tds: list = None) -> dict[str, int]:
    """Map table header text to td column index. Name is in th, so td order matches header order.
    Handles sites with redundant 'No.:N' column (Psaltoonalions, Simpson) by shifting indices."""
    col_map = {}
    td_idx = 0
    # If first row has redundant No. column (td[0]=number, td[1]=No.:number), we skip td[1]
    skip_index_1 = False
    if tds and _has_redundant_no_column(tds):
        skip_index_1 = True
    for h in header_texts:
        h_lower = (h or '').lower().strip()
        if not h_lower or h_lower == 'name':
            continue
        # When we have a redundant No. column, indices 1+ map to td 2+
        effective_idx = td_idx + (1 if skip_index_1 and td_idx >= 1 else 0)
        if h_lower in ('no.', 'no', '#') or 'number' in h_lower:
            col_map['number'] = 0  # Always first td when present
        elif h_lower in ('pos.', 'pos') or 'position' in h_lower:
            col_map['position'] = effective_idx
        elif h_lower in ('cl.', 'cl', 'class') or h_lower in ('yr.', 'yr'):
            col_map['class'] = effective_idx
        elif h_lower in ('ht.', 'ht') or 'height' in h_lower:
            col_map['height'] = effective_idx
        elif 'hometown' in h_lower or ('high school' in h_lower and 'club' not in h_lower) or 'previous school' in h_lower:
            col_map['town_hs'] = effective_idx
        elif ('major' in h_lower or 'minor' in h_lower) and 'club' not in h_lower:
            col_map['major'] = effective_idx
        td_idx += 1
    return col_map


def _parse_presto_table(soup: BeautifulSoup, school: str) -> list[dict]:
    """Parse PrestoSports table layout - uses header row to map columns reliably."""
    roster_data = []
    table = soup.select_one('.roster table') or soup.select_one('table')
    if not table:
        return []

    # Get header row from thead or first tr of tbody
    header_texts = []
    thead = table.find('thead')
    if thead:
        header_row = thead.find('tr')
        if header_row:
            for cell in header_row.find_all(['th', 'td']):
                header_texts.append(cell.get_text(strip=True))
    tbody = table.select_one('tbody') or table
    rows = tbody.find_all('tr')
    # Use first row's tds to detect redundant No. column (Psaltoonalions, Simpson)
    first_row_tds = []
    for r in rows:
        tds = r.find_all('td')
        if len(tds) >= 2:
            first_row_tds = tds
            break
    col_map = _map_headers_to_indices(header_texts, first_row_tds)

    # Fallback: if no header mapping, infer from common layouts
    if not col_map and rows:
        first_tds = rows[0].find_all('td')
        n = len(first_tds)
        col_map = {'number': 0, 'position': 1, 'class': 2, 'height': 3, 'town_hs': 5 if n >= 6 else 4}
        if n > 7:
            col_map['major'] = 7

    for row in rows:
        try:
            name_cell = row.find('th', class_='name') or row.find('th', attrs={'data-label': re.compile(r'name', re.I)}) or row.find('th')
            if not name_cell:
                continue
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
            if len(tds) < 3:
                continue

            def get_cell(field: str) -> str:
                idx = col_map.get(field)
                if idx is None or idx >= len(tds):
                    return ''
                raw = tds[idx].get_text(strip=True).replace('\n', ' ').replace('\t', ' ')
                prefixes = CELL_PREFIXES.get(field, [])
                return _strip_prefix(raw, prefixes)

            number = get_cell('number')
            pos = get_cell('position')
            cl = get_cell('class')
            ht = get_cell('height')
            town = highschool = ''
            town_hs_raw = get_cell('town_hs').replace('\r', ' ').strip()
            if town_hs_raw and '/' in town_hs_raw:
                parts = town_hs_raw.split('/', 1)
                town = parts[0].strip()
                highschool = parts[1].strip() if len(parts) > 1 else ''
            elif town_hs_raw:
                town = town_hs_raw
            major = get_cell('major')

            # Normalize height
            if ht and '-' in ht and '"' not in ht:
                ht = ht.replace('-', "'") + '"'

            roster_data.append({
                'name': player_name,
                'number': number,
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
