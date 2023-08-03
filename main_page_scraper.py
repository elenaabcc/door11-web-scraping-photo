import logging
import time
from selenium import webdriver
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

chrome_options = webdriver.ChromeOptions()
# this will disable image loading
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
# or alternatively we can set direct preference:
chrome_options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

# Web scrapper
driver = webdriver.Chrome(options=chrome_options)
base_url = "https://door11.com/?query-0-page="

# Loop through all 246 pages
for i in range(0, 246):
    url = base_url + str(i)
    driver.get(url)
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    # Get all the links
    urls = []
    for parent in soup.find_all(class_="wp-block-post-featured-image"):
        a_tag = parent.find("a")
        url = a_tag.attrs['href']
        urls.append(url)
        logging.info("URL: {}".format(url))

    # Save the URLs to an existing CSV file
    with open('collection_urls.csv', 'a') as f:
        for url in urls:
            f.write(url + "\n")

driver.close()
