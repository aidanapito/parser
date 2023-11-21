import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def fetch_html_with_selenium(url):
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait for the specific div to be present
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'stats-box'))
        WebDriverWait(driver, 10).until(element_present)
    except Exception as e:
        print(f"Error waiting for stats-box: {e}")
        driver.quit()
        return None

    # Get the HTML content after JavaScript execution
    html = driver.page_source

    # Close the webdriver
    driver.quit()

    return html

def parse_html_with_selenium(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find the div with the specified class
    stats_div = soup.find('div', class_='stats-box stats-box-alternate full clearfix')

    # Find the table within the div
    table = stats_div.find('table')

    # Define headers manually
    headers = ["NO.","Name", "Yr", "Pos", "m", "s", "k", "k/s", "e", "ta", "pct", "a", "a/s", "sa", "sa/s", "r", "re", "digs", "d/s",
               "bs", "ba", "tot", "b/s", "pts", "pts/s"]

    # Extract data rows
    data = []
    for row in table.find_all('tr'):
        try:
            # Extract player name and remove newline characters
            player_name = row.find('a').find('span').text.replace('\n', '').strip()
        except AttributeError:
            player_name = ''

        # Extract the rest of the row data
        row_data = [player_name] + [cell.text.strip() for cell in row.find_all(['td', 'th'])][1:]
        data.append(row_data)

    return headers, data

if __name__ == "__main__":
    url = 'https://www.wentworthathletics.com/sports/mvball/2022-23/teams/wentworth?view=lineup&r=0&pos='
    html = fetch_html_with_selenium(url)

    if html:
        headers, data = parse_html_with_selenium(html)

        # Create a DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Drop 'Yr' and 'Pos' columns
        df = df.drop(['Yr', 'Pos'], axis=1, errors='ignore')
        # Remove '\n' from the 'Name' column
        df['Name'] = df['Name'].str.replace('\n', '').str.replace(r'\s+', ' ').str.strip()

        # Print the DataFrame
        print(df)

        # Save the DataFrame to a CSV file
        df.to_csv('output.csv', index=False)