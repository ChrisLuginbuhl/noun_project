
#! python3
# noun_project_dl.py - Downloads every single APOD image, excludes non-image files.
# Chris Luginbuhl Mar 2019

import json
import requests
import os
import time
from tqdm import tqdm
import argparse

#source path of json, with trailing slash

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infile", help="Path to json from nounproject")
parser.add_argument("-o", "--outpath", help="Path to folder of downloaded images (will be created if it doesn't exist)")
parser.add_argument("-s", "--final_size", help="Size in pixels of resized images (square)", type=int)
parser.add_argument("-c", "--cropmode", help="Crop mode, 'f' or 'i' for Fit or fIll", default = 'f')
args = parser.parse_args()

print( "Infile {}, Output Path {}, Final Size {}, Crop Mode {} ".format(
        args.infile,
        args.outpath,
        args.final_size,
        args.cropmode
        ))

txt = open(args.infile)
with open(args.infile, 'r') as f:
    nouns_dict = json.load(f)



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

URL_values = extract_values(nouns_dict, 'preview_url')  #2nd parameter is the key that gives the URL
print("Found ", len(URL_values), " URLs.")
os.makedirs(args.outpath, exist_ok=True)                         # store imgs in subfolder

counter = 0
for noun_URL in tqdm(URL_values):
    if noun_URL is None:
        print('Could not find image.')
    else:
        # print('Downloading image %s...' % (noun_URL))
        resp = requests.get(noun_URL)
        resp.raise_for_status()
        #save the file
        imageFile = open(os.path.join(args.outpath, 'drone_' + str(counter)), 'wb')
        for chunk in resp.iter_content(100000):
            imageFile.write(chunk)
        imageFile.close()
        counter += 1
        time.sleep(1)  #prevents flooding the server with download activity. Int or float as argument
print('Done.')
