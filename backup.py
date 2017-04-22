import json
import os
import requests
import shutil
import sys
import datetime

USER_TOKEN = os.getenv('INSTAGRAM_TOKEN', None)
FEED_URI = 'https://api.instagram.com/v1/users/self/media/recent/'
SAVE_DIR = 'backup'
SAVE_JSON_DATA = False


def download_file(url, filename):
    # only download the file if it doesn't already exist
    if not os.path.isfile(filename):
        response = requests.get(url, stream=True)
        with open(filename, 'wb') as new_file:
            shutil.copyfileobj(response.raw, new_file)
        del response

def save_image(image):
    try:
        image_name = image['caption']['text']
    except TypeError:
        image_name = ''

    print 'Fetching %s' % (image_name)
    image_url = image['images']['standard_resolution']['url']

    formatted_date = datetime.datetime.fromtimestamp(int(image['created_time'])).strftime('%m-%d-%Y')
    image_name = '%s %s' % (formatted_date, image_name)
    image_path = '%s/%s.jpg' % (SAVE_DIR, image_name)
    download_file(image_url, image_path)

    if image['type'] == 'video':
        video_url = image['videos']['standard_resolution']['url']
        video_filename = '%s/%s.mp4' % (SAVE_DIR, image_name)
        download_file(video_url, video_filename)

    # save the data as JSON
    if SAVE_JSON_DATA == True:
        data_filename = '%s/%s.json' % (SAVE_DIR, image_name)
        with open(data_filename, 'w') as data_file:
            json.dump(image, data_file, sort_keys=True, indent=4)

if USER_TOKEN is None:
    sys.exit("Requires INSTAGRAM_USER_TOKEN environment variable.")

max_id = 0
while max_id is not None:
    url = '%s?access_token=%s' % (FEED_URI, USER_TOKEN)
    if max_id:
        url += '&max_id=%s' % max_id

    data = requests.get(url)
    response = data.json()

    for image in response['data']:
        save_image(image)

    try:
        max_id = response['pagination']['next_max_id']
    except KeyError:
        max_id = None
