"""
Simple Spotify Data Collector - Using Public Playlists
This is a more reliable alternative that collects from curated mood-based playlists
"""

import os
from dotenv import load_dotenv
from spotify_data_collector import SpotifyDataCollector

# Load credentials
load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_client_id_here')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_client_secret_here')

# Validate credentials
if CLIENT_ID == 'your_client_id_here' or CLIENT_SECRET == 'your_client_secret_here':
    print("❌ Please set up your Spotify credentials in .env file")
    print("See CREDENTIALS_SETUP.md for instructions")
    exit(1)

# Initialize collector
print("Initializing Spotify collector...")
collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
print("✓ Connected to Spotify API\n")

# Curated mood-based playlists from Spotify
# These are public playlists that work reliably
mood_playlists = {
    'happy_energetic': [
        '37i9dQZF1DX3rxVfibe1L0',  # Mood Booster
        '37i9dQZF1DXdPec7aLTmlC',  # Happy Hits
        '37i9dQZF1DX0UrRvztWcAU',  # Feelin' Good
    ],
    'happy_calm': [
        '37i9dQZF1DX3YSRoSdA634',  # Chill Hits
        '37i9dQZF1DWZqd5JICZI0u',  # Happy Vibes
        '37i9dQZF1DX4WYpdgoIcn6',  # Chill Vibes
    ],
    'sad_calm': [
        '37i9dQZF1DWSqBruwoIXkA',  # Life Sucks
        '37i9dQZF1DX7qK8ma5wgG1',  # Sad Indie
        '37i9dQZF1DX3YSRoSdA634',  # Sad Hour
    ],
    'energetic': [
        '37i9dQZF1DX76Wlfdnj7AP',  # Beast Mode
        '37i9dQZF1DX0pH2SQMRXnC',  # Pumped Pop
        '37i9dQZF1DXdxcBWuJkbcy',  # Power Workout
    ],
    'calm': [
        '37i9dQZF1DWZd79rJ6a7lp',  # Peaceful Piano
        '37i9dQZF1DX4sWSpwq3LiO',  # Peaceful Guitar
        '37i9dQZF1DX3Ogo9pFvBkY',  # Calming Acoustic
    ]
}

print("=" * 70)
print("COLLECTING TRACKS FROM MOOD-BASED PLAYLISTS")
print("=" * 70)
print(f"This will collect from {sum(len(p) for p in mood_playlists.values())} playlists")
print("=" * 70)
print()

all_tracks = []

for mood, playlist_ids in mood_playlists.items():
    print(f"📂 Collecting {mood} tracks...")
    
    for i, playlist_id in enumerate(playlist_ids, 1):
        try:
            print(f"  - Playlist {i}/{len(playlist_ids)}...", end=' ')
            tracks = collector.get_playlist_tracks(playlist_id)
            
            # Add mood category to each track
            for track in tracks:
                track['mood_category'] = mood
            
            all_tracks.extend(tracks)
            print(f"✓ Got {len(tracks)} tracks")
            
        except Exception as e:
            print(f"⚠️  Error: {str(e)[:50]}...")
            continue
    
    print()

# Get unique track IDs
print("=" * 70)
print("PROCESSING COLLECTED TRACKS")
print("=" * 70)

track_ids = list(set([t['track_id'] for t in all_tracks]))
print(f"Total tracks collected: {len(all_tracks)}")
print(f"Unique tracks: {len(track_ids)}")

# Get audio features
print("\nFetching audio features...")
audio_features = collector.get_audio_features(track_ids)
print(f"✓ Got audio features for {len(audio_features)} tracks")

# Create feature lookup
features_dict = {f['id']: f for f in audio_features}

# Combine track info with audio features
combined_data = []
for track in all_tracks:
    if track['track_id'] in features_dict:
        features = features_dict[track['track_id']]
        combined = {**track, **features}
        combined_data.append(combined)

# Create DataFrame
import pandas as pd
df = pd.DataFrame(combined_data)

# Keep only relevant columns
columns_to_keep = [
    'track_id', 'name', 'artist', 'album', 'popularity', 'duration_ms',
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'mood_category'
]
df = df[columns_to_keep]

# Remove duplicates (keep first occurrence)
df = df.drop_duplicates(subset=['track_id'], keep='first')

# Save to CSV
output_file = 'spotify_mood_dataset.csv'
df.to_csv(output_file, index=False)

# Display results
print("\n" + "=" * 70)
print("COLLECTION COMPLETE!")
print("=" * 70)
print(f"\n✓ Dataset saved to: {output_file}")
print(f"✓ Total tracks: {len(df)}")
print(f"\nTracks per mood category:")
print(df['mood_category'].value_counts().to_string())

print(f"\nAudio features summary:")
print(df[['valence', 'energy', 'danceability', 'tempo']].describe())

print("\n" + "=" * 70)
print("You can now use this dataset for your MoodShift recommendation system!")
print("=" * 70)
