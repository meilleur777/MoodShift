"""
Alternative Spotify Collector - Uses Track Analysis Instead
This bypasses the audio_features endpoint completely
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
print("ALTERNATIVE SPOTIFY COLLECTOR")
print("Using Track Analysis API (bypasses audio_features endpoint)")
print("=" * 70)

# Initialize
print("\n✓ Connecting to Spotify...")
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))
print("✓ Connected!\n")

# Search categories with mood keywords
searches = {
    'happy_energetic': ['upbeat pop 2024', 'party dance hits', 'feel good music'],
    'happy_calm': ['peaceful acoustic', 'chill morning', 'happy indie folk'],
    'sad_calm': ['sad piano', 'emotional ballad', 'melancholy songs'],
    'sad_energetic': ['intense rock', 'aggressive metal', 'dark electronic'],
    'neutral': ['top 50 global', 'trending now', 'popular music']
}

all_tracks = []

print(f"🎵 Searching for tracks...")
print("=" * 70)

for mood, queries in searches.items():
    print(f"\n📂 Collecting {mood} tracks...")
    
    for query in queries:
        try:
            print(f"  Searching '{query}'...", end=' ')
            results = sp.search(q=query, type='track', limit=50, market='US')
            
            if results and 'tracks' in results:
                count = 0
                for track in results['tracks']['items']:
                    if track and track.get('id'):
                        all_tracks.append({
                            'track_id': track['id'],
                            'name': track['name'],
                            'artist': ', '.join([a['name'] for a in track['artists']]),
                            'album': track['album']['name'],
                            'popularity': track['popularity'],
                            'duration_ms': track['duration_ms'],
                            'explicit': track.get('explicit', False),
                            'release_date': track['album'].get('release_date', ''),
                            'mood_category': mood
                        })
                        count += 1
                
                print(f"✓ {count} tracks")
            else:
                print("⚠️  No results")
            
            time.sleep(0.2)
            
        except Exception as e:
            print(f"⚠️  Error: {str(e)[:50]}")

print(f"\n✓ Total collected: {len(all_tracks)} tracks")

# Remove duplicates
print("🔄 Removing duplicates...", end=' ')
seen = set()
unique_tracks = []
for track in all_tracks:
    if track['track_id'] not in seen:
        seen.add(track['track_id'])
        unique_tracks.append(track)

print(f"✓ {len(unique_tracks)} unique tracks")

# Try to get audio features using alternative method
print("\n📊 Attempting to get audio features...")
print("   Method 1: audio_features endpoint...", end=' ')

try:
    # Try a small batch first
    test_ids = [t['track_id'] for t in unique_tracks[:5]]
    test_features = sp.audio_features(test_ids)
    
    if test_features and any(f is not None for f in test_features):
        print("✓ Working!")
        print("   Getting features for all tracks...")
        
        # Get all features in batches
        all_features = []
        batch_size = 50
        
        for i in range(0, len(unique_tracks), batch_size):
            batch_ids = [t['track_id'] for t in unique_tracks[i:i+batch_size]]
            batch_num = (i // batch_size) + 1
            total_batches = (len(unique_tracks) + batch_size - 1) // batch_size
            
            print(f"   [{batch_num}/{total_batches}] ", end='', flush=True)
            
            try:
                features = sp.audio_features(batch_ids)
                if features:
                    all_features.extend([f for f in features if f is not None])
                    print(f"✓ {len([f for f in features if f])} features")
                time.sleep(0.3)
            except:
                print("⚠️  Failed")
                continue
        
        # Create feature lookup
        if all_features:
            features_dict = {f['id']: f for f in all_features}
            
            # Add features to tracks
            for track in unique_tracks:
                if track['track_id'] in features_dict:
                    f = features_dict[track['track_id']]
                    track.update({
                        'danceability': f.get('danceability'),
                        'energy': f.get('energy'),
                        'key': f.get('key'),
                        'loudness': f.get('loudness'),
                        'mode': f.get('mode'),
                        'speechiness': f.get('speechiness'),
                        'acousticness': f.get('acousticness'),
                        'instrumentalness': f.get('instrumentalness'),
                        'liveness': f.get('liveness'),
                        'valence': f.get('valence'),
                        'tempo': f.get('tempo')
                    })
            
            print(f"\n   ✓ Added features to {len(all_features)} tracks")
            has_features = True
        else:
            print("\n   ⚠️  No features retrieved")
            has_features = False
    else:
        print("❌ Blocked")
        has_features = False
        
except Exception as e:
    print(f"❌ Error: {str(e)[:50]}")
    has_features = False

# If audio_features failed, use track analysis (different endpoint)
if not has_features:
    print("\n   Method 2: track analysis endpoint...", end=' ')
    
    try:
        # Try analysis endpoint (different from audio_features)
        test_track = unique_tracks[0]['track_id']
        analysis = sp.audio_analysis(test_track)
        
        if analysis:
            print("✓ Working!")
            print("   ⚠️  Note: This endpoint is slower and gives different data")
            print("   Collecting analysis for tracks (this may take a while)...")
            
            for i, track in enumerate(unique_tracks[:100]):  # Limit to 100 for speed
                try:
                    print(f"   [{i+1}/100] {track['name'][:30]}...", end=' ')
                    analysis = sp.audio_analysis(track['track_id'])
                    
                    if analysis and 'track' in analysis:
                        t = analysis['track']
                        # Analysis gives different but useful data
                        track.update({
                            'tempo': t.get('tempo'),
                            'loudness': t.get('loudness'),
                            'key': t.get('key'),
                            'mode': t.get('mode'),
                            'time_signature': t.get('time_signature')
                        })
                        print("✓")
                    else:
                        print("⚠️")
                    
                    time.sleep(0.5)  # Be nice to API
                    
                except:
                    print("❌")
                    continue
            
            has_features = True
        else:
            print("❌ Also blocked")
            has_features = False
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        has_features = False

# If still no features, estimate from available data
if not has_features:
    print("\n   Method 3: Estimating from available data...")
    
    for track in unique_tracks:
        # Estimate based on mood category and other factors
        mood = track['mood_category']
        popularity = track['popularity'] / 100.0
        
        # Simple heuristic estimates
        if mood == 'happy_energetic':
            track['valence'] = 0.7 + (popularity * 0.2)
            track['energy'] = 0.7 + (popularity * 0.2)
        elif mood == 'happy_calm':
            track['valence'] = 0.7 + (popularity * 0.2)
            track['energy'] = 0.3 + (popularity * 0.1)
        elif mood == 'sad_calm':
            track['valence'] = 0.2 + (popularity * 0.1)
            track['energy'] = 0.2 + (popularity * 0.1)
        elif mood == 'sad_energetic':
            track['valence'] = 0.2 + (popularity * 0.1)
            track['energy'] = 0.7 + (popularity * 0.2)
        else:  # neutral
            track['valence'] = 0.5
            track['energy'] = 0.5
    
    print("   ✓ Created estimated values based on mood categories")
    print("   ⚠️  Note: These are estimates, not real audio features")

# Create DataFrame
df = pd.DataFrame(unique_tracks)

# Save
output_file = 'spotify_mood_dataset.csv'
df.to_csv(output_file, index=False)

# Display results
print("\n" + "=" * 70)
print("✅ COLLECTION COMPLETE!")
print("=" * 70)
print(f"\n📁 Saved to: {output_file}")
print(f"📊 Total tracks: {len(df)}")

print(f"\n🎭 Tracks per mood:")
mood_counts = df['mood_category'].value_counts()
for mood, count in mood_counts.items():
    print(f"   {mood:20s} {count:4d} tracks")

if has_features and 'valence' in df.columns:
    print(f"\n📈 Audio features:")
    available_features = [col for col in ['valence', 'energy', 'tempo', 'danceability'] 
                         if col in df.columns and df[col].notna().any()]
    if available_features:
        print(f"   ✓ Available: {', '.join(available_features)}")
        summary = df[available_features].describe().loc[['mean', 'std']]
        print(summary.to_string())
else:
    print(f"\n⚠️  Audio features:")
    print(f"   Using estimated values based on mood categories")
    print(f"   Real features unavailable due to API restrictions")

print("\n" + "=" * 70)
print("🎉 Dataset ready for MoodShift!")
print("=" * 70)
print("\nYou can now use this dataset with:")
print("  cd ../moodshift-core")
print("  python main.py --current-mood sad_calm --target-mood happy_energetic")
print("\n" + "=" * 70)
