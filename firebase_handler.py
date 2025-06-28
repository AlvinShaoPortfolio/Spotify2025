import firebase_admin 

from firebase_admin import credentials, firestore #auth app using a service account key and working with firestore db

cred = credentials.Certificate("firebaseKey.json") #loads private key

firebase_admin.initialize_app(cred) #initialize app with private key

db = firestore.client() #firestore client object. Lets you interact with the db basically

def store_claimed_song(user_id, user_name, song_info):
    user_ref = db.collection("users").document(str(user_id))

    user_ref.set({"name": user_name}, merge = True) #merge to avoid overwriting data

    song_ref = user_ref.collection("claimed_songs").document(song_info["name"]) #where the storage reference is

    song_ref.set({ #storing song info
        "song_name": song_info["name"],
        "artist_name": song_info["artist"],
        "album_name": song_info["album"],
        "points": song_info["points"],
    })

def cache_artist_songs(artist_id, artist_name, songs):
    doc_ref = db.collection("artists").document(artist_id) #storing artist reference under their artist_id

    doc_ref.set({
        "name": artist_name,
        "songs": songs
    })

def get_cached_artist(artist_id):
    doc = db.collection("artists").document(artist_id).get()
    if doc.exists:
        return doc.to_dict().get("songs", [])
    return None

