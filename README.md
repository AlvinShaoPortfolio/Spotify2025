# Spotify2025   

import random

# --- Example track list (stream) ---
tracks = [
    {"name": "Mega Hit",    "popularity": 95},
    {"name": "Deep Cut 1",  "popularity": 20},
    {"name": "Deep Cut 2",  "popularity": 15},
    {"name": "Average Tune","popularity": 50},
    {"name": "Hidden Gem",  "popularity":  5},
]

# --- Streaming weighted pick setup ---
total_weight = 0
chosen_track = None

# We’ll invert popularity so that lower-popularity → higher weight:
MAX_POP = 100

for track in tracks:
    # compute rarity weight
    w = (MAX_POP + 1) - track["popularity"]
    # update running total
    total_weight += w
    # decide whether to replace chosen_track
    # with probability w / total_weight
    if random.random() * total_weight < w:
        chosen_track = track

# --- Result ---
print(f"You got: {chosen_track['name']} (pop: {chosen_track['popularity']})")
