import time
from selenium import webdriver
from bs4 import BeautifulSoup

# * Template for js enabled websites, will scrape whatever you want to scrape

def get_data(soup):
    """
    Extract data from a BeautifulSoup object and return it.
    This function should be customized for each specific scraping task.
    """
    # TODO: Implement this function
    pass

def scrape_pages(base_url, num_pages):
    """
    Scrape multiple pages of a website using Selenium and BeautifulSoup.
    """

    driver = webdriver.Firefox()
    all_data = []

    for i in range(num_pages):
        driver.get(base_url + str(i*10))
        driver.implicitly_wait(10)
        html = driver.page_source
        time.sleep(5)
        soup = BeautifulSoup(html, 'html.parser')
        page_data = get_data(soup)
        all_data.extend(page_data)

    driver.quit()

    return all_data

def main():
    base_url = "https://www.example.com/page?start="
    num_pages = 5
    data = scrape_pages(base_url, num_pages)
    for item in data:
        print(item)

# TODO : Implement some way of storing that data
# If storing in csv, how do we check for and remove duplicates to reduce computation

if __name__ == "__main__":
    main()