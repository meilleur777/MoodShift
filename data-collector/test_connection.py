"""
Minimal Test - Verify Your Spotify Credentials Work
This gets just 10 tracks to test everything is working
"""

import os
from dotenv import load_dotenv
from spotify_data_collector import SpotifyDataCollector

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

if not CLIENT_ID or not CLIENT_SECRET:
    print("❌ Credentials not found in .env file")
    exit(1)

print("=" * 60)
print("MINIMAL TEST - Getting 10 tracks")
print("=" * 60)

try:
    # Test 1: Connect
    print("\n1️⃣  Testing connection...", end=' ')
    collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
    print("✓ Connected!")
    
    # Test 2: Search for tracks
    print("2️⃣  Searching for tracks...", end=' ')
    results = collector.sp.search(q='pop', type='track', limit=10)
    tracks = results['tracks']['items']
    print(f"✓ Found {len(tracks)} tracks")
    
    # Test 3: Get audio features
    print("3️⃣  Getting audio features...", end=' ')
    track_ids = [t['id'] for t in tracks if t]
    features = collector.get_audio_features(track_ids)
    print(f"✓ Got {len(features)} features")
    
    # Show sample
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Everything works!")
    print("=" * 60)
    print("\nSample track:")
    if features:
        f = features[0]
        print(f"  Track ID: {f['id']}")
        print(f"  Valence: {f['valence']:.3f} (happiness)")
        print(f"  Energy:  {f['energy']:.3f} (intensity)")
        print(f"  Tempo:   {f['tempo']:.1f} BPM")
    
    print("\n" + "=" * 60)
    print("🎉 Your setup is working perfectly!")
    print("=" * 60)
    print("\nYou can now run:")
    print("  python ultra_simple_collector.py")
    print("\nThis will collect 500-800 tracks for your dataset.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check your .env file has correct credentials")
    print("  2. Make sure CLIENT_SECRET is 32 characters")
    print("  3. No spaces or quotes in .env file")
    print("  4. Wait a few minutes if you hit rate limit")
