"""
Add Audio Features to Existing Dataset
Run this after the 403 error is resolved (usually after 30-60 minutes)
"""

import os
from dotenv import load_dotenv
from spotify_data_collector import SpotifyDataCollector
import pandas as pd

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

print("=" * 70)
print("ADD AUDIO FEATURES TO DATASET")
print("=" * 70)

# Check if basic dataset exists
import os.path
if not os.path.isfile('spotify_basic_dataset.csv'):
    print("\n❌ Error: spotify_basic_dataset.csv not found")
    print("\nRun workaround_collector.py first to create the basic dataset")
    exit(1)

# Load existing dataset
print("\n📂 Loading existing dataset...")
df = pd.read_csv('spotify_basic_dataset.csv')
print(f"✓ Loaded {len(df)} tracks")

# Initialize collector
print("\n🔗 Connecting to Spotify...")
try:
    collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
    print("✓ Connected!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Test if audio features work now
print("\n🧪 Testing if audio features API is working...")
test_id = df['track_id'].iloc[0]
try:
    test_features = collector.sp.audio_features([test_id])
    if test_features and test_features[0]:
        print("✓ Audio features API is working!")
    else:
        print("⚠️  Audio features returned None")
        print("The API might still be rate-limited. Wait longer and try again.")
        exit(1)
except Exception as e:
    print(f"❌ Still getting errors: {e}")
    print("\nThe API is still rate-limited or having issues.")
    print("Please wait longer (30-60 minutes) and try again.")
    exit(1)

# Get audio features
print(f"\n📊 Fetching audio features for {len(df)} tracks...")
print("This may take several minutes...\n")

track_ids = df['track_id'].tolist()
audio_features = collector.get_audio_features(track_ids)

if not audio_features:
    print("❌ No audio features retrieved")
    exit(1)

print(f"\n✓ Retrieved features for {len(audio_features)} tracks")

# Create features dict
features_dict = {f['id']: f for f in audio_features}

# Add features to dataframe
print("🔗 Adding features to dataset...", end=' ')

for idx, row in df.iterrows():
    track_id = row['track_id']
    if track_id in features_dict:
        f = features_dict[track_id]
        df.at[idx, 'danceability'] = f.get('danceability')
        df.at[idx, 'energy'] = f.get('energy')
        df.at[idx, 'key'] = f.get('key')
        df.at[idx, 'loudness'] = f.get('loudness')
        df.at[idx, 'mode'] = f.get('mode')
        df.at[idx, 'speechiness'] = f.get('speechiness')
        df.at[idx, 'acousticness'] = f.get('acousticness')
        df.at[idx, 'instrumentalness'] = f.get('instrumentalness')
        df.at[idx, 'liveness'] = f.get('liveness')
        df.at[idx, 'valence'] = f.get('valence')
        df.at[idx, 'tempo'] = f.get('tempo')

print("✓ Done")

# Remove tracks without features
print("🧹 Cleaning up...", end=' ')
df_with_features = df.dropna(subset=['valence', 'energy'])
print(f"✓ {len(df_with_features)} tracks with complete features")

# Save complete dataset
output_file = 'spotify_mood_dataset.csv'
df_with_features.to_csv(output_file, index=False)

# Display results
print("\n" + "=" * 70)
print("✅ SUCCESS! Audio features added!")
print("=" * 70)
print(f"\n📁 Saved to: {output_file}")
print(f"📊 Total tracks: {len(df_with_features)}")

print(f"\n🎭 Tracks per mood:")
print(df_with_features['mood_category'].value_counts().to_string())

print(f"\n📈 Audio features summary:")
feature_cols = ['valence', 'energy', 'danceability', 'tempo']
print(df_with_features[feature_cols].describe().round(3).to_string())

print("\n" + "=" * 70)
print("🎉 Your dataset is now complete and ready to use!")
print("=" * 70)
print("\nNext steps:")
print("  1. Run: python analyzer.py")
print("  2. Check the generated visualizations")
print("  3. Start building your MoodShift recommendation system!")
print("\n" + "=" * 70)
