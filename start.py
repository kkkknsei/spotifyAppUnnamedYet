# First of all, this project got three scripts: one for dealing with the search and one for dealing with the playlist

# This first one, the search script, was written as I started the project and I wanted to leave it that way for some
# reasons:

# 1. For you to see how I escalated (this project took me almost two weeks and I think I improved enough while doing
# this)

# 2. Because it's the v1.0 of this project, I can improve it for sure but if I continue doing this I'll never release it
# 3. Because then I'll have a "guide" to know what things I need to write and test again

# Last, The "info.py" file is for you to fill while using/testing, you'll need a Spotify account and access to
# "Soptify Developers"

# My goal on doing this was to learn how to handle an API and I think I managed to learn it, hope you enjoy.

import random
from bs4 import BeautifulSoup
import requests
import datetime
from urllib.parse import urlencode
import base64
import json
import time
import os
import subprocess
from info import client_id, client_secret

# Needed information and variables
start_time = time.time()
user_url = input("Input a Album List:")
req = requests.get(user_url, headers={'User-agent': 'your bot 0.1'})  # getting the HTML from the user's input
soup = BeautifulSoup(req.text, "lxml")  # switching it to text
albums_info = []
link_count = 0

# This next line has a problem: only lists with this HTML structure will be processed more of less right
for heading in soup.find_all("h2"):
    albums_info.append(len(albums_info) + 1)
    albums_info[len(albums_info) - 1] = heading.text.strip()

# Saving the albums on a txt temp file
with open("temp.txt", mode='wt', encoding='utf-8') as f:
    for i in range(len(albums_info)):
        replacechars = ":()"
        for character in replacechars:
            albums_info[i] = albums_info[i].replace(character, "")
        f.write(albums_info[i] + '\n')

# This is important: Sometimes there will be a difference on the number of albums on the list and the amount returned
# This can happen for different reasons: may be because of the albums is not on spotify, may be because of the code's
# flaw
# I'll have a more serious look at it as I'll develop it more

print(f"Returned Albums from List: {len(albums_info)}")


# In the "playlist_handle.py" file I'll get more into it but basically this class is used to authenticate the user:
class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret == None or client_id == None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            return False
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True


# Auth
spotify = SpotifyAPI(client_id, client_secret)
spotify.perform_auth()
access_token = spotify.access_token

# headers needed for authenticating the user while doing something (like creating a playlist or searching for whatever)
headers = {
    "Authorization": f"Bearer {access_token}"
}

# the count of found tracks
found_links = 0

# opening the albums' temp file and searching for albums' ids (and then saving on another temp file) I can also use
# lists to do it. As I said, there are something I can improve on it but as it's functional, this is the v1.0
with open("temp.txt", "r") as tempfile:
    with open("links.txt", mode='wt', encoding='utf-8') as linksfile:
        for row in tempfile:
            albums_stored_data = ''.join([i for i in row if not i.isdigit()])
            endpoint = "https://api.spotify.com/v1/search"
            data = urlencode({"q": f"{albums_stored_data}", "type": "album"})
            lookup_url = f"{endpoint}?{data}"
            r = requests.get(lookup_url, headers=headers)
            if r.status_code != 200:
                print(f"Error {r.status_code} while searching for {data.split('=')}")

            jason = json.dumps(r.json())
            for row in jason.split('"'):
                if "spotify:album:" in row:
                    linksfile.write(row + '\n')
                    found_links += 1
                    break

# tracks counting
tracks_count = 0

# opening the albums' links and getting 4 tracks from each one

with open("links.txt", "r") as linksfile:
    with open("tracks.txt", mode='wt', encoding='utf-8') as tracksfile:
        for row in linksfile:
            tracks = []  # this will store the tracks ids from one album at time for iterating over every album
            album_id = row.split("spotify:album:")[1][:-1]
            data = urlencode({"q": f"{album_id}", "type": "track"})
            endpoint = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
            lookup_url = f"{endpoint}?limit=25"  # will only return 25 tracks from albums, I think it's an acceptable
            # number

            # the limit on endpoint is 25, so I'll use 26 as default value for storing random.randint
            store_random = 26
            r = requests.get(lookup_url, headers=headers)
            if r.status_code != 200:
                print(f"Error {r.status_code} while searching for {data.split('=')}")

            jason = json.dumps(r.json())
            for row in jason.split('"'):
                if "https://open.spotify.com/track/" in row:
                    tracks.append(len(tracks) + 1)
                    tracks[len(tracks) - 1] = row

            for i in range(4):  # using random to get random tracks
                randomize = random.randint(0, (len(tracks) - 1))
                if randomize != store_random:  # making sure that one tracks isn't picked two times (but that needs
                    # an improvement)
                    tracksfile.write(tracks[randomize] + '\n')
                    store_random = randomize
                    tracks_count += 1

# calling "playlist_handle.py"
cmd = 'python playlist_handle.py'

p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
out, err = p.communicate()
result = out.split('\n'.encode())
for lin in result:
    if not lin.startswith('#'.encode()):
        print(lin)


# printing the results with all info collected


def results():
    albums_deficit = len(albums_info) - found_links
    tracks_deficit = (found_links * 4) - tracks_count

    print(f"The application found {found_links} albums and {tracks_count} tracks on Spotify")
    if albums_deficit > 0 or tracks_deficit > 0:
        print(f"Albums deficit: {albums_deficit}")
        print(f"Tracks deficit: {tracks_deficit} (relative to the found albums)")

    # Removing the temp files

    os.remove("temp.txt")
    os.remove("links.txt")
    os.remove("tracks.txt")


results()

print("The application took %s seconds to finish." % (time.time() - start_time))
