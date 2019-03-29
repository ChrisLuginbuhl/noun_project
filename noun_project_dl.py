
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
import noun_project_config

NUM_REQUESTS = 40     #API returns up to 50 results. How many times to request
START_OFFSET = 400   #Offset for filename and for API request, skipping images already acquired
URLS_PER_REQUEST = 50
auth = OAuth1(noun_project_config.api_key, noun_project_config.api_secret)
endpoint = "https://api.thenounproject.com/icons/drone?limit=50&offset=" #this API returns up to 50 results

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="Path to json from nounproject", default = None)
parser.add_argument("-o", "--outpath", help="Path to folder of downloaded images (will be created if it doesn't exist)")
parser.add_argument("-s", "--finalsize", help="Size in pixels of resized images (square)", type=int)
args = parser.parse_args()

print( "Infile {}, Output Path {}, Final Size {}".format(
        args.infile,
        args.outpath,
        args.finalsize,
        ))



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
    for noun_URL in tqdm(URLs):
        if noun_URL is None:
            print('Could not find image.')
        else:
            # print('Downloading image %s...' % (noun_URL))
            resp = requests.get(noun_URL)
            resp.raise_for_status()
            #save the file
            imageFile = open(os.path.join(args.outpath, 'drone_' + str(counter)) + '.png', 'wb')
            for chunk in resp.iter_content(100000):
                imageFile.write(chunk)
            imageFile.close()
            counter += 1
            time.sleep(0.15)  #prevents flooding the server with download activity. Int or float as argument
#end get_images

def record_attribution(names_list):
    attribFile = open(os.path.join(args.outpath, 'attribution' + '.txt'), 'a')  # append mode
    for name in names_list:
        attribFile.write(name + '\n')
        #print(name)
    attribFile.close()
# end record_attribution()

os.makedirs(args.outpath, exist_ok=True)                         # store imgs in subfolder
for i in range(NUM_REQUESTS):
    nouns_dict = get_json(START_OFFSET + i * URLS_PER_REQUEST)
    URL_values = extract_values(nouns_dict, 'preview_url')  #2nd parameter is the dictionary key that gives the URL
    names_list = extract_values(nouns_dict, 'attribution')
    print("Found ", len(URL_values), " URLs.")
    get_images(URL_values, START_OFFSET + i * URLS_PER_REQUEST)
    record_attribution(names_list)
    if ((args.infile == None) & (len(URL_values) != URLS_PER_REQUEST)):
        break
print("Done.")
