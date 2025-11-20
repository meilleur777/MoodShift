"""
Smart Spotify Data Collector - Searches for Mood Playlists Automatically
This collector finds public playlists by searching for mood keywords
"""

import os
from dotenv import load_dotenv
from spotify_data_collector import SpotifyDataCollector
import pandas as pd
import time

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
print("=" * 70)
print("SMART MOOD-BASED MUSIC COLLECTOR")
print("=" * 70)
print("\nInitializing Spotify collector...")
collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
print("✓ Connected to Spotify API\n")

# Mood-based search queries
# We'll search for tracks directly using these keywords
mood_searches = {
    'happy_energetic': ['happy pop', 'upbeat dance', 'party hits', 'feel good'],
    'happy_calm': ['acoustic happy', 'peaceful happy', 'chill happy', 'indie happy'],
    'sad_calm': ['sad acoustic', 'melancholy', 'sad indie', 'emotional ballad'],
    'sad_energetic': ['angry rock', 'intense metal', 'aggressive rap', 'dark electronic'],
    'neutral': ['top hits', 'popular music', 'trending songs', 'new releases']
}

print("=" * 70)
print("SEARCHING FOR MOOD-BASED TRACKS")
print("=" * 70)
print(f"Will search for tracks across {len(mood_searches)} mood categories")
print("=" * 70)
print()

all_tracks = []
tracks_per_mood = 100  # Target number of tracks per mood

for mood, search_queries in mood_searches.items():
    print(f"🎵 Searching for {mood} tracks...")
    mood_tracks = []
    
    for query in search_queries:
        try:
            print(f"  - Searching '{query}'...", end=' ')
            
            # Search for tracks
            results = collector.sp.search(q=query, type='track', limit=50)
            
            if results and 'tracks' in results and 'items' in results['tracks']:
                tracks = results['tracks']['items']
                
                for track in tracks:
                    if track and track.get('id'):
                        mood_tracks.append({
                            'track_id': track['id'],
                            'name': track['name'],
                            'artist': ', '.join([artist['name'] for artist in track['artists']]),
                            'album': track['album']['name'],
                            'popularity': track['popularity'],
                            'duration_ms': track['duration_ms'],
                            'mood_category': mood
                        })
                
                print(f"✓ Found {len(tracks)} tracks")
            else:
                print("⚠️  No results")
            
            time.sleep(0.2)  # Rate limiting
            
            # Stop if we have enough tracks for this mood
            if len(mood_tracks) >= tracks_per_mood:
                break
                
        except Exception as e:
            print(f"⚠️  Error: {str(e)[:50]}...")
            continue
    
    all_tracks.extend(mood_tracks[:tracks_per_mood])
    print(f"  → Collected {len(mood_tracks[:tracks_per_mood])} tracks for {mood}\n")

# Get unique track IDs
print("=" * 70)
print("PROCESSING COLLECTED TRACKS")
print("=" * 70)

# Remove duplicates while preserving mood category
seen_ids = set()
unique_tracks = []
for track in all_tracks:
    if track['track_id'] not in seen_ids:
        seen_ids.add(track['track_id'])
        unique_tracks.append(track)

print(f"Total tracks collected: {len(all_tracks)}")
print(f"Unique tracks: {len(unique_tracks)}")

# Get audio features
print("\nFetching audio features...")
track_ids = [t['track_id'] for t in unique_tracks]
audio_features = collector.get_audio_features(track_ids)
print(f"✓ Got audio features for {len(audio_features)} tracks")

# Create feature lookup
features_dict = {f['id']: f for f in audio_features}

# Combine track info with audio features
combined_data = []
for track in unique_tracks:
    if track['track_id'] in features_dict:
        features = features_dict[track['track_id']]
        combined = {**track, **features}
        combined_data.append(combined)

# Create DataFrame
df = pd.DataFrame(combined_data)

# Keep only relevant columns
columns_to_keep = [
    'track_id', 'name', 'artist', 'album', 'popularity', 'duration_ms',
    'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
    'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
    'mood_category'
]
df = df[columns_to_keep]

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

print(f"\n📊 Audio features summary (valence & energy):")
print(df.groupby('mood_category')[['valence', 'energy']].mean().round(3))

print(f"\n📈 Overall statistics:")
print(df[['valence', 'energy', 'danceability', 'tempo']].describe().round(3))

print("\n" + "=" * 70)
print("✅ SUCCESS! You can now use this dataset for MoodShift")
print("=" * 70)
print("\nNext steps:")
print("  1. Run: python analyzer.py")
print("  2. Check the mood_space.png visualization")
print("  3. Start building your recommendation system!")
print("=" * 70)
