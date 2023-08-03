import logging
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import csv

logging.basicConfig(level=logging.INFO)

chrome_options = webdriver.ChromeOptions()
# this will disable image loading
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
# or alternatively we can set direct preference:
chrome_options.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

# Run headless
chrome_options.add_argument('--headless')

# Web scrapper
driver = webdriver.Chrome(options=chrome_options)

collection_images_is_empty = False

collection_images_file = 'collection_images.csv'

# Read the last line of the CSV file. If the file is empty, write the header
with open(collection_images_file, 'r') as f:
    last_line = f.readlines()[-1]
    if last_line == '':
        collection_images_is_empty = True

last_url = ''
to_already_to_skip = False
if collection_images_is_empty:
    # Write the header
    with open(collection_images_file, 'a') as f:
        writer = csv.writer(f)
        writer.writerow(['collection_url', 'image_url', 'image_alt'])
else:
    # Of the last row get the first column
    last_url = last_line.split(',')[0]
    to_already_to_skip = True
    logging.info("Last URL: {}".format(last_url))


# Open "collection_urls.csv" and for each URL, extract all the images
def download_images(collection_url) -> Exception:
    try:
        driver.get(collection_url)
        time.sleep(2)

        # Split the URL to get the collection name
        collection_name = collection_url.split('/')[-2]
        logging.info("Collection name: {}".format(collection_name))

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the div tag with the class name 'pgcsimplygalleryblock-masonry-content'
        div_tag = soup.find('div', {'class': 'pgcsimplygalleryblock-masonry-content'})

        # Find all the image tags inside the div tag
        images = div_tag.find_all('img')
        images_urls = {}
        for image in images:
            src = image.attrs['src']
            if src == "https://media.door11.com/wp-content/uploads/2022/06/DOOR11-logo-BETA.png?lossy=1&ssl=1":
                continue

            # Remove the query string from the image url
            src = src.split('?')[0]

            # Check if the image as an alt attribute
            if 'alt' in image.attrs:
                alt = image.attrs['alt']
                images_urls[src] = alt
                logging.info("src:{} - alt:{}".format(src, alt))
            else:
                images_urls[src] = ''
                logging.info("src:{} - alt:{}".format(src, ''))

        # Save the URLs to an existing CSV file
        with open('collection_images.csv', 'a') as collection_images_f:
            collection_images_writer = csv.writer(collection_images_f)
            for src, alt in images_urls.items():
                collection_images_writer.writerow([collection_url, src, alt])
    except Exception as e:
        return e


with open('collection_urls.csv', 'r') as coll_urls_file:
    for url in coll_urls_file:
        # Remove the newline character
        url = url.rstrip()

        # If toAlreadyToSkip is True, skip the URL
        if to_already_to_skip:
            if url == last_url:
                to_already_to_skip = False
            continue

        is_time_to_exit = False
        while not is_time_to_exit:
            exception = download_images(url)
            if exception is not None:
                logging.error("Exception: {}".format(exception))
                logging.info("Retrying. Restarting the driver...")
                # Web scrapper
                driver = webdriver.Chrome(options=chrome_options)
                time.sleep(5)
            else:
                is_time_to_exit = True

driver.close()
