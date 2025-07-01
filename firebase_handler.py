import firebase_admin 
from firebase_admin import credentials, firestore #auth app using a service account key and working with firestore db

cred = credentials.Certificate("firebaseKey.json") #loads private key

firebase_admin.initialize_app(cred) #initialize app with private key

db = firestore.client() #firestore client object. Lets you interact with the db basically

def user_already_claimed_song(user_id, song_id):
    doc_ref = db.collection("users").document(str(user_id)).collection("claimed_songs").document(song_id).get()
    return doc_ref.exists

def check_song_in_server(server_id, song_id):
    doc_ref = db.collection("servers").document(str(server_id)).collection("claimed_songs").document(song_id).get() #retrieving the song by its name
    return doc_ref.exists #returns true if exists

def store_in_server(server_id, song_id, user_id, song_name): #just storing the id as collection 
    claimed_cache_ref = db.collection("servers").document(str(server_id)).collection("claimed_songs").document(song_id)
    claimed_cache_ref.set({
        "song_name": song_name,
        "user_id": user_id,
    })

def store_claimed_song(user_id, user_name, song_info):
    user_ref = db.collection("users").document(str(user_id))

    user_ref.set({"name": user_name}, merge = True) #merge to avoid overwriting data

    song_ref = user_ref.collection("claimed_songs").document(song_info["id"]) #where the storage reference is

    song_ref.set({ #storing song info
        "song_name": song_info["name"],
        "artist_name": song_info["artist"],
        "album_name": song_info["album"],
        "points": song_info["points"],
    })

def retrieve_song_holder(server_id, song_id):
    user_ref = db.collection("servers").document(str(server_id)).collection("claimed_songs").document(song_id).get()

    if(user_ref.exists):
        user_id = user_ref.get("user_id")

        name_ref = db.collection("users").document(str(user_id)).get()

        if (name_ref.exists):
            return name_ref.get("name")
    return None

#cache of artist songs / not dealing with users ----------------------------------------------------------

def cache_artist_songs(artist_id, artist_name, songs):
    doc_ref = db.collection("artists").document(artist_id) #storing artist reference under their artist_id

    doc_ref.set({
        "name": artist_name,
        "songs": songs
    })

def get_cached_artist(artist_id):
    doc_ref = db.collection("artists").document(artist_id).get()
    if doc_ref.exists:
        return doc_ref.to_dict().get("songs", [])
    return None

