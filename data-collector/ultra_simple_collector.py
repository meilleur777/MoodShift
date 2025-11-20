"""
Ultra-Simple Spotify Collector
Gets popular tracks and classifies them by their audio features
This is the most reliable method - it always works!
"""

import os
from dotenv import load_dotenv
from spotify_data_collector import SpotifyDataCollector
import pandas as pd

# Load credentials
load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', 'your_client_id_here')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', 'your_client_secret_here')

# Validate credentials
if CLIENT_ID == 'your_client_id_here' or CLIENT_SECRET == 'your_client_secret_here':
    print("❌ Please set up your Spotify credentials in .env file")
    exit(1)

print("=" * 70)
print("ULTRA-SIMPLE SPOTIFY MUSIC COLLECTOR")
print("=" * 70)
print("This collector gets popular tracks and classifies them by mood")
print("=" * 70)

# Initialize collector
print("\n✓ Connecting to Spotify...")
collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
print("✓ Connected!\n")

# Search categories that will give us diverse music
search_terms = [
    'pop', 'rock', 'hip hop', 'electronic', 'indie',
    'jazz', 'classical', 'country', 'r&b', 'reggae',
    'metal', 'folk', 'soul', 'blues', 'latin',
    'dance', 'acoustic', 'chill', 'party', 'workout'
]

print(f"🎵 Searching {len(search_terms)} music categories...")
print("=" * 70)

all_tracks = []

for i, term in enumerate(search_terms, 1):
    print(f"[{i}/{len(search_terms)}] Searching '{term}'...", end=' ')
    
    try:
        # Search for tracks
        results = collector.sp.search(q=term, type='track', limit=50)
        
        if results and 'tracks' in results:
            tracks = results['tracks']['items']
            
            for track in tracks:
                if track and track.get('id'):
                    all_tracks.append({
                        'track_id': track['id'],
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms']
                    })
            
            print(f"✓ Got {len(tracks)} tracks")
        else:
            print("⚠️  No results")
            
    except Exception as e:
        print(f"⚠️  Error: {str(e)[:50]}")

print(f"\n✓ Total tracks found: {len(all_tracks)}")

# Remove duplicates
print("🔄 Removing duplicates...", end=' ')
seen = set()
unique_tracks = []
for track in all_tracks:
    if track['track_id'] not in seen:
        seen.add(track['track_id'])
        unique_tracks.append(track)

print(f"✓ Kept {len(unique_tracks)} unique tracks")

# Get audio features
print("\n📊 Fetching audio features (this may take a few minutes)...")
print("=" * 70)
track_ids = [t['track_id'] for t in unique_tracks]
audio_features = collector.get_audio_features(track_ids)
print("=" * 70)
print(f"✓ Got features for {len(audio_features)} tracks")

# Combine data
print("🔗 Combining data...", end=' ')
features_dict = {f['id']: f for f in audio_features}
combined_data = []

for track in unique_tracks:
    if track['track_id'] in features_dict:
        features = features_dict[track['track_id']]
        combined = {**track, **features}
        combined_data.append(combined)

print(f"✓ {len(combined_data)} tracks with features")

# Create DataFrame
df = pd.DataFrame(combined_data)

# Classify into moods based on valence and energy
print("\n🎭 Classifying tracks into moods...", end=' ')

def classify_mood(row):
    """Classify based on Russell's Circumplex Model"""
    valence = row['valence']
    energy = row['energy']
    
    if valence >= 0.6 and energy >= 0.6:
        return 'happy_energetic'
    elif valence >= 0.6 and energy < 0.4:
        return 'happy_calm'
    elif valence < 0.4 and energy < 0.4:
        return 'sad_calm'
    elif valence < 0.4 and energy >= 0.6:
        return 'sad_energetic'
    else:
        return 'neutral'

df['mood_category'] = df.apply(classify_mood, axis=1)
print("✓ Done")

# Keep relevant columns
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
print("✅ COLLECTION COMPLETE!")
print("=" * 70)
print(f"\n📁 Saved to: {output_file}")
print(f"📊 Total tracks: {len(df)}")

print(f"\n🎭 Tracks per mood category:")
mood_counts = df['mood_category'].value_counts()
for mood, count in mood_counts.items():
    percentage = (count / len(df) * 100)
    print(f"   {mood:20s} {count:4d} tracks ({percentage:.1f}%)")

print(f"\n📈 Mood characteristics (valence & energy):")
mood_stats = df.groupby('mood_category')[['valence', 'energy']].mean()
print(mood_stats.round(3).to_string())

print(f"\n🎵 Sample tracks from each mood:")
for mood in df['mood_category'].unique():
    sample = df[df['mood_category'] == mood].iloc[0]
    print(f"   {mood:20s} → {sample['name'][:40]} by {sample['artist'][:30]}")

print("\n" + "=" * 70)
print("🎉 SUCCESS! Your dataset is ready!")
print("=" * 70)
print("\nWhat to do next:")
print("  1. Analyze: python analyzer.py")
print("  2. Check visualizations in the generated PNG files")
print("  3. Start building your MoodShift recommendation system!")
print("\n" + "=" * 70)
