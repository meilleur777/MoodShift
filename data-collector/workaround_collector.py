"""
Workaround Collector - Gets data without using audio_features endpoint
This works even if you're getting 403 errors on audio features
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_client_id_here')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_client_secret_here')

if CLIENT_ID == 'your_client_id_here' or CLIENT_SECRET == 'your_client_secret_here':
    print("❌ Please set up your Spotify credentials in .env file")
    exit(1)

print("=" * 70)
print("WORKAROUND COLLECTOR (No Audio Features API)")
print("=" * 70)
print("This collector works even with 403 errors on audio features")
print("It collects basic track info that can still be used for recommendations")
print("=" * 70)

# Initialize
print("\n✓ Connecting to Spotify...")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))
print("✓ Connected!\n")

# Search categories
search_terms = [
    'happy pop', 'energetic dance', 'upbeat party',  # Happy energetic
    'acoustic chill', 'peaceful folk', 'calm indie',  # Happy calm
    'sad piano', 'melancholy acoustic', 'emotional ballad',  # Sad calm
    'intense rock', 'aggressive metal', 'dark electronic',  # Sad energetic
    'top hits', 'popular music', 'trending songs'  # Neutral
]

mood_map = {
    0: 'happy_energetic', 1: 'happy_energetic', 2: 'happy_energetic',
    3: 'happy_calm', 4: 'happy_calm', 5: 'happy_calm',
    6: 'sad_calm', 7: 'sad_calm', 8: 'sad_calm',
    9: 'sad_energetic', 10: 'sad_energetic', 11: 'sad_energetic',
    12: 'neutral', 13: 'neutral', 14: 'neutral'
}

print(f"🎵 Searching {len(search_terms)} categories...")
print("=" * 70)

all_tracks = []

for i, term in enumerate(search_terms):
    print(f"[{i+1}/{len(search_terms)}] '{term}'...", end=' ')
    
    try:
        results = sp.search(q=term, type='track', limit=50, market='US')
        
        if results and 'tracks' in results:
            for track in results['tracks']['items']:
                if track and track.get('id'):
                    # Extract available info
                    all_tracks.append({
                        'track_id': track['id'],
                        'name': track['name'],
                        'artist': ', '.join([a['name'] for a in track['artists']]),
                        'album': track['album']['name'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms'],
                        'explicit': track.get('explicit', False),
                        'release_date': track['album'].get('release_date', ''),
                        'mood_category': mood_map.get(i, 'neutral')
                    })
            
            print(f"✓ Got {len(results['tracks']['items'])} tracks")
        else:
            print("⚠️  No results")
        
        time.sleep(0.2)
            
    except Exception as e:
        print(f"⚠️  Error: {str(e)[:50]}")

print(f"\n✓ Total: {len(all_tracks)} tracks")

# Remove duplicates
print("🔄 Removing duplicates...", end=' ')
seen = set()
unique_tracks = []
for track in all_tracks:
    if track['track_id'] not in seen:
        seen.add(track['track_id'])
        unique_tracks.append(track)

print(f"✓ {len(unique_tracks)} unique tracks")

# Create DataFrame
df = pd.DataFrame(unique_tracks)

# Add derived features from available data
print("📊 Computing derived features...", end=' ')

# Estimate energy from duration and popularity
# (This is a rough approximation, not as good as real audio features)
df['estimated_energy'] = (df['popularity'] / 100.0)
df['estimated_tempo'] = 120.0  # Default tempo

print("✓ Done")

# Save
output_file = 'spotify_basic_dataset.csv'
df.to_csv(output_file, index=False)

# Display results
print("\n" + "=" * 70)
print("✅ COLLECTION COMPLETE!")
print("=" * 70)
print(f"\n📁 Saved to: {output_file}")
print(f"📊 Total tracks: {len(df)}")

print(f"\n🎭 Tracks per mood category:")
mood_counts = df['mood_category'].value_counts()
for mood, count in mood_counts.items():
    print(f"   {mood:20s} {count:4d} tracks")

print(f"\n📈 Available features:")
print(f"   ✓ Track ID, name, artist, album")
print(f"   ✓ Popularity (0-100)")
print(f"   ✓ Duration")
print(f"   ✓ Release date")
print(f"   ✓ Mood category (from search terms)")
print(f"   ⚠️  No audio features (valence, energy, etc.)")

print("\n" + "=" * 70)
print("📝 NEXT STEPS")
print("=" * 70)
print("\nThis dataset doesn't have audio features, but you can still:")
print("  1. Use it for basic collaborative filtering")
print("  2. Use mood categories from search terms")
print("  3. Use popularity and duration as features")
print("\nTo get audio features later:")
print("  1. Wait 30-60 minutes (API rate limit)")
print("  2. Run: python diagnose.py")
print("  3. If it works, run: python add_audio_features.py")

print("\n" + "=" * 70)
