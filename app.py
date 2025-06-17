import requests #allows me to make http requests
import os #lets me access env variables
import random
from dotenv import load_dotenv #lets me load the env file

load_dotenv() #load env file into memory

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

artist_List = ["Kendrick Lamar"]

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials", #app level access not user account level
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }

    response = requests.post(url, headers=headers, data=data, auth=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))

    if response.status_code != 200:
        print("Failed to get token")
        print("Response:", response.text)

    response.raise_for_status()
    return response.json()["access_token"]

def get_artist_ID(name, token, limit = 1): #artistID is a string
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": name,
        "type": "artist",
        "limit": limit
    }
    response = requests.get(url, headers = headers, params = params)
    response.raise_for_status()

    return response.json()["artists"]["items"][0]["id"]

def get_artist_albums_info(id, token, limit = 50): #api call the album ids along with the number of tracks
    url = f"https://api.spotify.com/v1/artists/{id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "include_groups": "album,single", #must be album,single no space idk why compiler needs it to be like that
        "limit": limit
    }

    list_of_album_info = []
    while(url != None):
        response = requests.get(url, headers = headers, params = params)
        response.raise_for_status()

        list_of_albums = response.json()

        for album in list_of_albums["items"]:
            list_of_album_info.append({
                "name": album["name"],
                "id" : album["id"],
            })
        url = list_of_albums.get("next")
    return list_of_album_info

def get_album_songs(album_info, token, limit = 50):
    url = f"https://api.spotify.com/v1/albums/{album_info.get("id")}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "limit": limit
    }

    response = requests.get(url, headers = headers, params = params)
    response.raise_for_status()

    album_songs = response.json()

    list_of_songs = []

    for song in album_songs["items"]:
        list_of_songs.append({
            "name": song["name"],
            "id": song["id"]
        })
    return list_of_songs

def get_list_of_songs(artist_ID, token):
    list_of_album_infos = get_artist_albums_info(artist_ID, token)

    seen_songs = set()
    list_of_songs = list()
    excluded_keywords = {"remix", "instrumental", "radio", "acoustic", "mix", "- live", "dub"}

    for album in list_of_album_infos: #maybe possible to get lower timp comp? not sure how though to improve 
        songs_in_album = get_album_songs(album, token)

        for song in songs_in_album:
            if (song["name"] not in seen_songs) and not any(keyword in song["name"].lower() for keyword in excluded_keywords):
                seen_songs.add(song["name"])
                list_of_songs.append(song)

    return list_of_songs





if __name__ == "__main__":  
    token = get_access_token()

    artist_ID = get_artist_ID(random.choice(artist_List), token) #Get the artists Identification based off of their name

    if(artist_ID == None):
        print("No artists found")
   
    list_of_songs = get_list_of_songs(artist_ID, token)

    print(list_of_songs["name"])

   