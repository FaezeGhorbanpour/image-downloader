import pandas as pd
import requests
import shutil
from bs4 import BeautifulSoup
import json
# import webarchive
import os
# import get_wayback_machine
import numpy as np


def insta_downloader(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    metaTag = soup.find_all('meta', {'property': 'og:image'})
    imgURL = metaTag[0]['content']
    return imgURL


def save_image(url, final_path):
    try:
        r = requests.get(url, stream=True)
        with open(final_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    except:
        print('hi')
        raise Exception


def waybackpach_downloader(url):
    command = 'waybackpack --list --uniques-only ' + url
    response = os.popen(command).read().split('\n')
    valid_response = {len(r): r for r in response}
    result = valid_response[max(valid_response.keys())]
    return result


def download_image(i, url, path):
    furl = url
    print(i)
    if url:
        try:
            r = requests.get(url, stream=True)
            if r.status_code == 200:
                if 'instagram' in url:
                    url = insta_downloader(url)
            else:
                url = waybackpach_downloader(url)
            save_image(url, path)
            print('done ')
            return True
        except:
            try:
                if 'web.archive' in furl:
                    purl = "".join(url.split('_')[1:])[1:]
                    return download_image(i, purl, path)
                if url:
                    url = waybackpach_downloader(url)
                    save_image(url, path)
                    print('done !')
                    return True
                else:
                    print('failed ', furl)
                    return False
            except Exception as e:
                print('failed', furl)
                print(e)
                return False


if __name__ == '__main__':
    files = ['politifact.csv', 'gossipcop.csv']
    status = []
    for f in files:
        data = pd.read_csv(f)
        data.dropna(subset=['image_url'], inplace=True)
        for i, row in data.iterrows():
            if row['image_url']:
                image_name = row['image_url'].split('/')[-1].split('?')[0]
                img = download_image(i, row['image_url'], '/images/' + image_name)
                if img:
                    status.append(image_name)
                else:
                    status.append(None)
        data['status'] = pd.DataFrame(status)[0]
        print('number of all data is', data.shape[0])
        data.dropna(subset=['status'], inplace=True)
        data.to_csv(f)
        print('number of downloaded image is', data.shape[0])
        print()
