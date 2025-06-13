import requests #allows me to make http requests
import os #lets me access env variables
from dotenv import load_dotenv #lets me load the env file


load_dotenv() #load env file into memory

def get_access_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
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


if __name__ == "__main__":
    token = get_access_token()
    print("Access token:", token)
