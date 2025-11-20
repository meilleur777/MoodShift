"""
Diagnostic Script - Figure out why we're getting 403 errors
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

print("=" * 70)
print("SPOTIFY API DIAGNOSTIC TEST")
print("=" * 70)

# Test 1: Basic connection
print("\n1️⃣  Testing basic connection...")
try:
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    ))
    print("   ✓ Connected to Spotify API")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    exit(1)

# Test 2: Search for a track
print("\n2️⃣  Testing search...")
try:
    results = sp.search(q='happy', type='track', limit=1)
    if results and 'tracks' in results and results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_id = track['id']
        track_name = track['name']
        artist_name = track['artists'][0]['name']
        print(f"   ✓ Found track: '{track_name}' by {artist_name}")
        print(f"   ✓ Track ID: {track_id}")
    else:
        print("   ❌ No tracks found")
        exit(1)
except Exception as e:
    print(f"   ❌ Search failed: {e}")
    exit(1)

# Test 3: Get audio features - Method 1 (list)
print("\n3️⃣  Testing audio features (method 1: list)...")
try:
    features = sp.audio_features([track_id])
    if features and features[0]:
        print(f"   ✓ Got features!")
        print(f"   ✓ Valence: {features[0]['valence']:.3f}")
        print(f"   ✓ Energy: {features[0]['energy']:.3f}")
        method1_works = True
    else:
        print("   ⚠️  No features returned")
        method1_works = False
except Exception as e:
    print(f"   ❌ Failed: {e}")
    method1_works = False

# Test 4: Get audio features - Method 2 (single track)
print("\n4️⃣  Testing audio features (method 2: single)...")
try:
    features = sp.audio_features(track_id)
    if features and features[0]:
        print(f"   ✓ Got features!")
        print(f"   ✓ Valence: {features[0]['valence']:.3f}")
        print(f"   ✓ Energy: {features[0]['energy']:.3f}")
        method2_works = True
    else:
        print("   ⚠️  No features returned")
        method2_works = False
except Exception as e:
    print(f"   ❌ Failed: {e}")
    method2_works = False

# Test 5: Get multiple audio features
print("\n5️⃣  Testing multiple audio features...")
try:
    # Get a few more tracks
    results = sp.search(q='pop', type='track', limit=5)
    track_ids = [t['id'] for t in results['tracks']['items'] if t]
    
    print(f"   Testing with {len(track_ids)} track IDs...")
    features = sp.audio_features(track_ids)
    
    if features:
        valid = [f for f in features if f is not None]
        print(f"   ✓ Got {len(valid)} features out of {len(track_ids)} tracks")
        multiple_works = True
    else:
        print("   ⚠️  No features returned")
        multiple_works = False
except Exception as e:
    print(f"   ❌ Failed: {e}")
    print(f"   Error details: {str(e)}")
    multiple_works = False

# Test 6: Check API scope/permissions
print("\n6️⃣  Checking API permissions...")
try:
    # Try to get current user (this requires different auth)
    user = sp.current_user()
    print("   ⚠️  User auth detected (not needed for this app)")
except:
    print("   ✓ Using Client Credentials flow (correct)")

# Summary
print("\n" + "=" * 70)
print("DIAGNOSTIC SUMMARY")
print("=" * 70)
print(f"Search API:              {'✓ Working' if True else '❌ Failed'}")
print(f"Audio Features (list):   {'✓ Working' if method1_works else '❌ Failed'}")
print(f"Audio Features (single): {'✓ Working' if method2_works else '❌ Failed'}")
print(f"Multiple Features:       {'✓ Working' if multiple_works else '❌ Failed'}")

if not multiple_works:
    print("\n" + "=" * 70)
    print("⚠️  ISSUE DETECTED")
    print("=" * 70)
    print("\nThe audio_features endpoint is returning 403 errors.")
    print("\nPossible causes:")
    print("1. Your Spotify app doesn't have the right permissions")
    print("2. Your account has reached API rate limits")
    print("3. There's a temporary Spotify API issue")
    print("\nSolutions to try:")
    print("\n📌 Solution 1: Wait and retry")
    print("   - Wait 30 minutes")
    print("   - Run this test again")
    print("   - Rate limits reset hourly")
    
    print("\n📌 Solution 2: Create a new Spotify app")
    print("   1. Go to: https://developer.spotify.com/dashboard")
    print("   2. Create a NEW app (call it 'MoodShift2')")
    print("   3. Get the new Client ID and Secret")
    print("   4. Update your .env file")
    
    print("\n📌 Solution 3: Use a workaround")
    print("   - We can collect data without audio features first")
    print("   - Then add features later when API works")
else:
    print("\n✅ Everything is working!")
    print("\nYou can now run:")
    print("  python ultra_simple_collector.py")

print("\n" + "=" * 70)
