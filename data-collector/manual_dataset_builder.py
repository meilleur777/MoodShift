"""
Manual Dataset Builder
Use this if Spotify API is completely blocked
Creates a dataset from track searches with estimated mood values
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import time

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

print("=" * 70)
print("MANUAL DATASET BUILDER")
print("Creates dataset when audio features API is blocked")
print("=" * 70)

# Initialize
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# Mood-based searches with expected characteristics
searches = [
    # Happy Energetic (high valence, high energy)
    {'query': 'upbeat pop 2024', 'mood': 'happy_energetic', 'valence': 0.8, 'energy': 0.8},
    {'query': 'dance party hits', 'mood': 'happy_energetic', 'valence': 0.85, 'energy': 0.85},
    {'query': 'feel good songs', 'mood': 'happy_energetic', 'valence': 0.8, 'energy': 0.75},
    
    # Happy Calm (high valence, low energy)
    {'query': 'acoustic chill', 'mood': 'happy_calm', 'valence': 0.7, 'energy': 0.3},
    {'query': 'peaceful morning', 'mood': 'happy_calm', 'valence': 0.75, 'energy': 0.35},
    {'query': 'indie folk calm', 'mood': 'happy_calm', 'valence': 0.7, 'energy': 0.3},
    
    # Sad Calm (low valence, low energy)
    {'query': 'sad piano', 'mood': 'sad_calm', 'valence': 0.2, 'energy': 0.25},
    {'query': 'emotional ballad', 'mood': 'sad_calm', 'valence': 0.25, 'energy': 0.3},
    {'query': 'melancholy acoustic', 'mood': 'sad_calm', 'valence': 0.2, 'energy': 0.25},
    
    # Sad Energetic (low valence, high energy)
    {'query': 'intense rock', 'mood': 'sad_energetic', 'valence': 0.3, 'energy': 0.75},
    {'query': 'aggressive metal', 'mood': 'sad_energetic', 'valence': 0.25, 'energy': 0.8},
    {'query': 'dark electronic', 'mood': 'sad_energetic', 'valence': 0.3, 'energy': 0.7},
    
    # Neutral
    {'query': 'top hits 2024', 'mood': 'neutral', 'valence': 0.5, 'energy': 0.5},
    {'query': 'popular music', 'mood': 'neutral', 'valence': 0.5, 'energy': 0.5},
]

all_tracks = []

print("\n🎵 Collecting tracks with estimated mood values...")
print("=" * 70)

for search_info in searches:
    query = search_info['query']
    mood = search_info['mood']
    base_valence = search_info['valence']
    base_energy = search_info['energy']
    
    print(f"\n'{query}'...", end=' ')
    
    try:
        results = sp.search(q=query, type='track', limit=50, market='US')
        
        if results and 'tracks' in results:
            count = 0
            for track in results['tracks']['items']:
                if track and track.get('id'):
                    # Add some variance to make it more realistic
                    variance = np.random.uniform(-0.1, 0.1)
                    valence = np.clip(base_valence + variance, 0, 1)
                    energy = np.clip(base_energy + variance, 0, 1)
                    
                    # Estimate other features
                    popularity = track['popularity'] / 100.0
                    
                    all_tracks.append({
                        'track_id': track['id'],
                        'name': track['name'],
                        'artist': ', '.join([a['name'] for a in track['artists']]),
                        'album': track['album']['name'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms'],
                        'mood_category': mood,
                        # Estimated audio features
                        'valence': round(valence, 3),
                        'energy': round(energy, 3),
                        'danceability': round(np.clip(base_energy + np.random.uniform(-0.15, 0.15), 0, 1), 3),
                        'acousticness': round(np.clip(0.5 - base_energy + np.random.uniform(-0.2, 0.2), 0, 1), 3),
                        'instrumentalness': round(np.random.uniform(0, 0.3), 3),
                        'speechiness': round(np.random.uniform(0.03, 0.15), 3),
                        'tempo': round(60 + (base_energy * 100) + np.random.uniform(-20, 20), 1),
                        'loudness': round(-60 + (base_energy * 50) + np.random.uniform(-5, 5), 2),
                        'liveness': round(np.random.uniform(0.05, 0.25), 3),
                        'key': np.random.randint(0, 12),
                        'mode': np.random.randint(0, 2)
                    })
                    count += 1
            
            print(f"✓ {count} tracks")
        else:
            print("⚠️  No results")
        
        time.sleep(0.2)
        
    except Exception as e:
        print(f"⚠️  Error: {str(e)[:50]}")

print(f"\n✓ Collected {len(all_tracks)} tracks")

# Remove duplicates
seen = set()
unique_tracks = []
for track in all_tracks:
    if track['track_id'] not in seen:
        seen.add(track['track_id'])
        unique_tracks.append(track)

print(f"✓ {len(unique_tracks)} unique tracks after deduplication")

# Create DataFrame
df = pd.DataFrame(unique_tracks)

# Save
output_file = 'spotify_mood_dataset.csv'
df.to_csv(output_file, index=False)

# Display results
print("\n" + "=" * 70)
print("✅ DATASET CREATED!")
print("=" * 70)
print(f"\n📁 Saved to: {output_file}")
print(f"📊 Total tracks: {len(df)}")

print(f"\n🎭 Tracks per mood:")
for mood, count in df['mood_category'].value_counts().items():
    print(f"   {mood:20s} {count:4d} tracks")

print(f"\n📈 Estimated audio features:")
print(df[['valence', 'energy', 'danceability', 'tempo']].describe().round(3))

print(f"\n⚠️  IMPORTANT NOTE:")
print("=" * 70)
print("This dataset uses ESTIMATED audio features based on mood categories.")
print("These are NOT real Spotify audio features, but educated guesses based on:")
print("  - Search query keywords")
print("  - Expected mood characteristics")
print("  - Random variance for realism")
print("\nThe dataset will still work with MoodShift, but accuracy may be lower.")
print("=" * 70)

print("\n🎯 Quality Assessment:")
valence_range = df.groupby('mood_category')['valence'].agg(['mean', 'std'])
energy_range = df.groupby('mood_category')['energy'].agg(['mean', 'std'])

print("\nValence by mood:")
print(valence_range.round(3))
print("\nEnergy by mood:")
print(energy_range.round(3))

print("\n" + "=" * 70)
print("✅ Dataset ready for MoodShift!")
print("=" * 70)
print("\nNext steps:")
print("  1. Copy to: moodshift/data/processed/spotify_mood_dataset.csv")
print("  2. Run: cd moodshift-core")
print("  3. Run: python main.py --current-mood sad_calm --target-mood happy_energetic")
print("\n" + "=" * 70)
