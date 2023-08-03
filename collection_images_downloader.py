import os
import csv
import time

import requests
from PIL import Image
import logging

# base_path = "images/"
# Get the path of external hdd
base_path = "./images/"

logging.basicConfig(level=logging.INFO)

collection_images_file = 'collection_images.csv'
collection_images_download_file = 'collection_images_download.csv'

# Read the last line of the CSV collection_images_download_file.
with open(collection_images_download_file, 'r') as f:
    last_line = f.readlines()[-1]
    if last_line != '':
        # Of the last row get the first column
        last_collection_url = last_line.split(',')[0]
        logging.info("Last URL: {}".format(last_collection_url))


# Write the header
# with open('collection_images_download.csv', 'a') as f:
#     writer = csv.writer(f)
#     writer.writerow(
#         ['collection_url', 'image_url', 'image_alt', 'image_name', 'image_path', 'image_size', 'image_width',
#          'image_height', 'image_format', 'image_mode'])

# download_image_data download the image from the URL and save it to a file. If data is None, retry the download.
def download_image_data(url, filename):
    status = None
    while status != 200:
        try:
            r = requests.get(url, stream=True, headers={'User-agent': 'Mozilla/5.0'})
            if r.status_code == 200:
                with open(filename, 'wb') as handler:
                    handler.write(r.content)
                status = 200
            else:
                logging.error("Image not downloaded: {}. Status: {}".format(url, r.status_code))
                # Sleep for 5 seconds
                time.sleep(5)
        except Exception as err:
            logging.error("Image not downloaded: {}. Error: {}".format(url, err))


with open('collection_images.csv', 'r') as f:
    reader = csv.reader(f)

    # Skip the header
    next(reader)

    to_already_to_skip = True

    for row in reader:
        newRow = row

        collection_url = row[0]

        # If toAlreadyToSkip is True, skip the URL
        if to_already_to_skip:
            if collection_url == last_collection_url:
                to_already_to_skip = False
            continue

        # Download the image
        logging.info("Downloading image: {}".format(row[1]))

        # Get the image collection name from the URL in the "collection_url" column
        collection_name = row[0].split('/')[-2]

        logging.info("Collection name: {}".format(collection_name))

        collection_path = base_path + collection_name
        # Create the folder if it doesn't exist
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        # Download the image in the folder
        image_name = os.path.basename(row[1])
        image_path = os.path.join(collection_path, image_name)

        # Download the image
        download_image_data(row[1], image_path)

        # Save the image name in the "image_name" column
        newRow.append(image_name)

        # Save the image path in the "image_path" column without the base path
        newRow.append(image_path.replace(base_path, ''))

        # Save the image size in the "image_size" column
        newRow.append(str(os.path.getsize(image_path)))

        try:
            # Save the image width in the "image_width" column
            with Image.open(image_path) as img:
                width, height = img.size
                newRow.append(str(width))

                # Save the image height in the "image_height" column
                newRow.append(str(height))

                # Save the image format in the "image_format" column
                newRow.append(img.format)

                # Save the image mode in the "image_mode" column
                newRow.append(img.mode)

                # Write the row to the CSV file
                with open('collection_images_download.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(newRow)

                logging.info("Image downloaded: {}".format(row[1]))

                # Close the image
                img.close()
        except Exception as e:
            logging.error("Image not valid: {}. Error: {}".format(row[1], e))

# Close the CSV file
f.close()
