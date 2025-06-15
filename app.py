import requests #allows me to make http requests
import os #lets me access env variables
import random
from dotenv import load_dotenv #lets me load the env file

load_dotenv() #load env file into memory

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

artist_List = ["Drake", "Kendrick Lamar", "Bruno Mars"]

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

def get_artist_albums_info(id, token): #api call the album ids along with the number of tracks
    url = f"https://api.spotify.com/v1/artists/{id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "include_groups": "album, single"
    }

    response = requests.get(url, headers = headers, params = params)
    response.raise_for_status()

    list_of_albums = response.json()["items"]

    album_IDS = []

    for album in list_of_albums:
        album_IDS.append({
            "id" : album["id"],
            "total_tracks" : album["total_tracks"]
        })
    return album_IDS

def get_album_songs(album, token, limit = 50):
    url = f"https://api.spotify.com/v1/albums/{album.get("id")}/tracks"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "limit": limit
    }

    response = requests.get(url, headers = headers, params = params)
    response.raise_for_status()

    list_of_songs = []

    for i in range(album.get("total_tracks")):
        list_of_songs.append(response.json()["items"][i]["name"])

    return list_of_songs

def get_artist_toptracks(id, token):
    url = f"https://api.spotify.com/v1/artists/{id}/top-tracks"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers = headers)
    response.raise_for_status()

    top_song_list = []

    for i in range(10):
        top_song_list.append(response.json()["tracks"][i]["name"])

    return top_song_list


if __name__ == "__main__":  
    token = get_access_token()

    artist_ID = get_artist_ID(random.choice(artist_List), token) #Get the artists Identification based off of their name

    if(artist_ID == None):
        print("No artists found")
   
    albums = get_artist_albums_info(artist_ID, token)

    set_of_songs = set()

    for album in albums:
        songs_in_album = get_album_songs(album, token)
        for song in songs_in_album:
            if song not in set_of_songs:
                set_of_songs.add(song)


    print(set_of_songs)
