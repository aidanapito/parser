from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests

# Define unique_links at a higher scope
unique_links = []

# Add a custom User-Agent header
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def create_url(year, month, day):
    return f"https://www.ncaa.com/scoreboard/volleyball-men/d3/{year:04d}/{month:02d}/{day:02d}/all-conf"

def fetch_content(url):
    try:
        # Include headers in the request
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content from {url}: {e}")
        return None
    
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the scoreboardGames container
    scoreboard_container = soup.find('div', {'id': 'scoreboardGames'})

    # Find all gamePod-link elements within the container
    game_links = scoreboard_container.find_all('a', {'class': 'gamePod-link'})

    for link in game_links:
        href = link['href']

        # Create a unique link using the base URL and the href
        base_url = "https://www.ncaa.com"
        unique_link = urljoin(base_url, href)

        # Add the unique link to the global list
        unique_links.append(unique_link)

    return unique_links

if __name__ == "__main__":
    year = 2023
    month = 1  # Change to the current date
    day = 13   # or any other day
    url = create_url(year, month, day)

    html = fetch_content(url)

    if html:
        unique_links = parse_html(html)

        # Print the list of unique links
        print("\nUnique Links:")
        for unique_link in unique_links:
            print(unique_link)