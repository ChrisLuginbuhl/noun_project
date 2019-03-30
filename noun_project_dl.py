
#! python3
# noun_project_dl.py - Downloads icons and their attributions from noun project.
# Chris Luginbuhl Mar 2019

import json
import requests
import os
import time
from tqdm import tqdm
import argparse
from requests_oauthlib import OAuth1
from PIL import Image
import noun_project_config

NUM_REQUESTS = 20      #How many times to request
START_OFFSET = 50*80      # Offset for filename and for API request, skipping images already acquired
URLS_PER_REQUEST = 50 # API returns up to 50 results.
CATEGORY = 'sun'      # modify this according to the type of icon you want to get.
auth = OAuth1(noun_project_config.api_key, noun_project_config.api_secret)
endpoint = "https://api.thenounproject.com/icons/" + CATEGORY + "?limit=" + str(URLS_PER_REQUEST) + "&offset="

lastBatchSize = 0
error404counter = 0


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="Path to json file from nounproject if not using API", default = None)
parser.add_argument("-o", "--outpath", help="Path to folder of downloaded images (will be created if it doesn't exist)", default = None)
parser.add_argument("-s", "--finalsize", help="Size in pixels of resized images (square)", default = None, type=int)
args = parser.parse_args()

print( "Infile {}, Output Path {}, Final Size {}".format(
        args.infile,
        args.outpath,
        args.finalsize,
        ))

if args.outpath == None:
    outpath = CATEGORY
else:
    outpath = args.outpath

def get_json(offset):
    if args.infile != None:
        txt = open(args.infile)
        with open(args.infile, 'r') as f:
            nouns = json.load(f) #dictionary type
    else:
        response = requests.get(endpoint + str(offset), auth=auth)
        nouns = response.json() #dictionary type

    return(nouns)

# end extract_json()

# this function came from https://hackersandslackers.com/extract-data-from-complex-json-python/
def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results
# end extract_values

def get_images(URLs, counter):
    global error404counter
    for noun_URL in tqdm(URLs):
        if noun_URL is None:
            print('Could not find image.')
        else:
            # print('Downloading image %s...' % (noun_URL))
            resp = requests.get(noun_URL)
            # resp.raise_for_status()  # if you want to throw an exception for a 404 or other error
            if not resp:
                error404counter += 1
                continue
            #save the file
            path_and_name = os.path.join(outpath, CATEGORY + '_' + str(counter))
            imageFile = open(path_and_name + '.png', 'wb')
            for chunk in resp.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
            png_to_jpg(path_and_name)
            counter += 1
            time.sleep(0.05)  #prevents flooding the server with download activity. Int or float as argument
#end get_images()

def png_to_jpg(filepath):
    im = Image.open(filepath + '.png')
    rgb_im = Image.new("RGB", im.size, "WHITE") #create white background
    rgb_im.paste(im, (0, 0), im)
    #rgb_im.convert('RGB')
    if args.finalsize != None:
        rgb_im = rgb_im.resize(finalsize, finalsize)
    rgb_im.save(filepath + '.jpg')
#end png_to_jpg()

def record_attribution(names_list):
    attribFile = open(os.path.join(outpath, 'attribution_' + CATEGORY + '.txt'), 'a')  # append mode
    for name in names_list:
        attribFile.write(name + '\n')
        #print(name)
    attribFile.close()
# end record_attribution()

os.makedirs(outpath, exist_ok=True)                         # store imgs in subfolder
for i in range(NUM_REQUESTS):
    nouns_dict = get_json(START_OFFSET + i * URLS_PER_REQUEST)
    URL_values = extract_values(nouns_dict, 'preview_url')  #2nd parameter is the dictionary key that gives the URL
    names_list = extract_values(nouns_dict, 'attribution')
    print("Found ", len(URL_values), " URLs.")
    get_images(URL_values, START_OFFSET + i * URLS_PER_REQUEST)
    record_attribution(names_list)
    if ((args.infile == None) & (len(URL_values) != URLS_PER_REQUEST)):
        lastBatchSize = len(URL_values)
        break
print("Got " + str((NUM_REQUESTS-1) * URLS_PER_REQUEST + lastBatchSize - error404counter) + " results, with " + str(error404counter) + "x 404 errors.")
