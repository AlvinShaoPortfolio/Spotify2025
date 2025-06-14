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

def get_artist_ID(name, token, limit = 1): #returns a string
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

def get_artist_tracks(id, token):
    url = f"https://api.spotify.com/v1/artists/{id}/top-tracks"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers = headers)
    response.raise_for_status()

    song_list = []

    for i in range(10):
        song_list.append(response.json()["tracks"][i]["name"])

    return song_list


if __name__ == "__main__":  
    token = get_access_token()

    artist_ID = get_artist_ID(random.choice(artist_List), token) #Get the artists Identification based off of their name

    if(artist_ID == None):
        print("No artists found")
    
    print(get_artist_tracks(artist_ID, token))
