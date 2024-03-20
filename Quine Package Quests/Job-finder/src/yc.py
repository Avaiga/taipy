import time
import logging
from selenium import webdriver
from bs4 import BeautifulSoup
import random
import pandas as pd
import datetime

# todo : yc 16 has some problems with the links, processed twice, add a check


date = datetime.datetime.now().strftime("%Y_%m_%d")
BASE_URL = "https://www.ycombinator.com/jobs/role"
driver = webdriver.Firefox()


def get_job_description(link):
    """
    Get the job description using the job links scraped."""
    try:
        # open a new tab and switch to it (substitute for context management)
        driver.execute_script('window.open("");')
        driver.switch_to.window(driver.window_handles[-1])
        # go to the page and parse it for description
        driver.get(link)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        description = soup.find("div", attrs={"class": "prose max-w-full"}).text
        # close the tab and go back to original window (job listings)
        time.sleep(10+random.random()*5)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return description

    except Exception as e:
        logging.exception(f"Exception {e} occured while getting JD")
        return None


def get_data(soup):
    containers = soup.findAll(
        "div",
        class_="mb-1 flex flex-col flex-nowrap items-center justify-between gap-y-2 md:flex-row md:gap-y-0",
    )

    jobs = []
    for container in containers:
        job_title_element = container.find("a", class_="font-semibold text-linkColor")

        if job_title_element:
            job_title = job_title_element.text
            link = job_title_element["href"]
            link = 'https://ycombinator.com' + link

        company_element = container.find("span", class_="block font-bold md:inline")
        if company_element:
            company = company_element.text

        location_element = container.find(
            "div",
            class_="border-r border-gray-300 px-2 first-of-type:pl-0 last-of-type:border-none last-of-type:pr-0",
        )
        if location_element:
            location = location_element.text

        date_posted_element = container.find(
            "span", class_="hidden text-sm text-gray-400 md:inline"
        )
        if date_posted_element:
            date_posted = date_posted_element.text.strip().split("(")[1].split(")")[0]

        job_description = get_job_description(link)

        jobs.append(
            {
                "title": job_title,
                "company": company,
                "location": location,
                "link": link,
                "description": job_description,
                "date": date,
            }
        )
    jobs = pd.DataFrame(jobs)
    return jobs


def scrape_pages(base_url, num_pages):
    all_data = pd.DataFrame()

    for _ in range(num_pages):
        driver.get(base_url)
        driver.implicitly_wait(15)
        html = driver.page_source
        time.sleep(3 + random.random() * 10)
        soup = BeautifulSoup(html, "html.parser")
        page_data = get_data(soup)
        all_data = pd.concat([all_data, page_data])

    driver.quit()
    all_data["query"] = all_data["title"]
    return all_data


def main():
    num_pages = 1
    data = scrape_pages(BASE_URL, num_pages)
    data["source"] = "yc"
    data.to_csv(f"data/raw/desc/{str(date)}desc_yc.csv", index=False)


if __name__ == "__main__":
    main()
