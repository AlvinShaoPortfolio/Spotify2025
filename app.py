import requests #allows me to make http requests
import os #lets me access env variables
import random
import aiohttp
import asyncio
#import time

from dotenv import load_dotenv #lets me load the env file

load_dotenv() #load env file into memory

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

artist_List = ["Billie Eilish"]
#start = time.time()

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

    #print("access_token Elapsed:", time.time() - start)

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

    #print("artist_ID Elapsed:", time.time() - start)

    return response.json()["artists"]["items"][0]["id"]

def get_artist_albums_info(id, token, limit = 50): #api call the album ids along with the number of tracks
    url = f"https://api.spotify.com/v1/artists/{id}/albums"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "include_groups": "album,single", #must be album,single no space idk why compiler needs it to be like that
        "limit": limit,
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

    #print("artist_albums_info Elapsed:", time.time() - start)

    return list_of_album_info

async def get_album_songs(session, album_info, token): #technically a dictionary with key name:id but it is liek a list
    url = f"https://api.spotify.com/v1/albums/{album_info.get("id")}/tracks"
    headers = {"Authorization": f"Bearer {token}"}

    async with session.get(url, headers = headers) as response:
        if response.status == 429:
            print("Rate limited by Spotify. Try again later.")
            return []
        
        response.raise_for_status()

        data = await response.json()
        return[{
            "name": track["name"], 
            "id": track["id"]
            }
            for track in data.get("items", [])
        ]

async def get_all_albums(album_infos, token):
    async with aiohttp.ClientSession() as session:
        tasks = [get_album_songs(session, album, token) for album in album_infos]
        results = await asyncio.gather(*tasks)
        return [track for album in results for track in album]

async def get_list_of_songs(artist_ID, token): #returns a list of ids that are not duplicates or have keyword errors
    list_of_album_infos = get_artist_albums_info(artist_ID, token, limit = 50)

    songs_in_album = await get_all_albums(list_of_album_infos, token)

    seen_songs = set()
    list_of_songs = list()
    excluded_keywords = {"remix", "instrumental", "radio", "acoustic", "mix", "- live", "dub", "- sped up", "- slow", "version", "live at"}

    for song in songs_in_album:
        if (song["name"] not in seen_songs) and not any(keyword in song["name"].lower() for keyword in excluded_keywords):
            seen_songs.add(song["name"])
            list_of_songs.append(song["id"])

    #print("list_of_songs Elapsed:", time.time() - start)

    return list_of_songs

def get_popularity(ids, token):
    url = "https://api.spotify.com/v1/tracks"
    headers = {"Authorization": f"Bearer {token}"}

    song_popularitys = []

    for i in range(0, len(ids), 50): #iterate through songs in chunks of 50 because the limit per api request is 50
        group = ids[i:i + 50] #setting the group of songs
        params = {
            "ids": ",".join(group)
        }
        
        response = requests.get(url, headers = headers, params = params)
        response.raise_for_status()

        all_songs = response.json()["tracks"]

        for song in all_songs:
            song_popularitys.append({
                "name": song["name"],
                "popularity": 101 - song["popularity"],
                "id": song["id"]
            })

    #print("popularity Elapsed:", time.time() - start)

    return song_popularitys

def get_song_with_popularity(popularity_list):
    songs = [song for song in popularity_list]
    weights = [song["popularity"] for song in songs]

    chosen = random.choices(songs, weights=weights, k=1)[0]

    #this commented out section is for the probability of getting the song
    #total_weight = sum(weights)
    #chosen_index = songs.index(chosen)
    #chosen_weight = weights[chosen_index]
    #chosen_chance = (chosen_weight / total_weight) * 100

    #print(f'Rolled: {chosen["name"]} with a {chosen_chance:.2f}% chance')
    #print("song_with_popularity Elapsed:", time.time() - start)
    return chosen

def get_album_image(song_id, token):
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers = headers)

    response.raise_for_status()

    track_info = response.json()

    #print("album_id Elapsed:", time.time() - start)
    image = track_info["album"]["images"][0]["url"]
    name = track_info["album"]["name"]

    return image, name

async def get_album_cover_and_name(): 
    token = get_access_token()

    chosen_artist_name = random.choice(artist_List)

    artist_ID = get_artist_ID(chosen_artist_name, token) #Get the artists Identification based off of their name

    if(artist_ID == None):
        return None, None, None, None, None

    list_of_songs_ids = await get_list_of_songs(artist_ID, token)
    popularity_list = get_popularity(list_of_songs_ids, token)
    chosen_song = get_song_with_popularity(popularity_list)

    album_cover, album_name = get_album_image(chosen_song["id"], token)
    song_points = int(2 ** ((101-chosen_song["popularity"])/10 ) / 2)

    return chosen_song["name"], album_cover, album_name, song_points, chosen_artist_name
    

   