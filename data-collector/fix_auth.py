"""
Fix for "No token provided" Spotify API Error
This script tests and fixes authentication issues
"""

import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

print("=" * 70)
print("SPOTIFY AUTHENTICATION FIX")
print("=" * 70)

# Load environment variables
load_dotenv()

# Get credentials
CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

print("\n1️⃣  Checking credentials...")
print(f"   CLIENT_ID: {CLIENT_ID[:10] if CLIENT_ID else 'NOT FOUND'}...{CLIENT_ID[-5:] if CLIENT_ID and len(CLIENT_ID) > 15 else ''}")
print(f"   CLIENT_SECRET: {'*' * 10 if CLIENT_SECRET else 'NOT FOUND'}...")

if not CLIENT_ID or not CLIENT_SECRET:
    print("\n❌ ERROR: Credentials not found!")
    print("\nYour .env file should contain:")
    print("   SPOTIFY_CLIENT_ID=your_id_here")
    print("   SPOTIFY_CLIENT_SECRET=your_secret_here")
    print("\nMake sure:")
    print("   - File is named exactly '.env' (with the dot)")
    print("   - File is in the same directory as this script")
    print("   - No spaces around the = sign")
    print("   - No quotes around the values")
    exit(1)

if CLIENT_ID == 'your_client_id_here' or CLIENT_SECRET == 'your_client_secret_here':
    print("\n❌ ERROR: Please update your credentials!")
    print("\nReplace the placeholder values with your actual Spotify credentials.")
    exit(1)

print("   ✓ Credentials found")

# Test authentication
print("\n2️⃣  Testing authentication...")

try:
    # Method 1: Using SpotifyClientCredentials
    auth_manager = SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
    
    # Force token request
    token_info = auth_manager.get_access_token(as_dict=False)
    
    if token_info:
        print("   ✓ Successfully obtained access token!")
        print(f"   Token: {token_info[:20]}...")
    else:
        print("   ❌ Failed to get token")
        exit(1)
        
except Exception as e:
    print(f"   ❌ Authentication failed: {e}")
    print("\n🔧 Possible solutions:")
    print("   1. Check your Client ID is correct")
    print("   2. Check your Client Secret is correct")
    print("   3. Make sure your Spotify app is not deleted")
    print("   4. Try creating a new Spotify app")
    exit(1)

# Test API call
print("\n3️⃣  Testing Spotify API connection...")

try:
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    # Simple test query
    results = sp.search(q='test', type='track', limit=1)
    
    if results and 'tracks' in results:
        print("   ✓ API connection successful!")
        track = results['tracks']['items'][0]
        print(f"   Test track: {track['name']} by {track['artists'][0]['name']}")
    else:
        print("   ⚠️  API returned empty results")
        
except Exception as e:
    print(f"   ❌ API call failed: {e}")
    exit(1)

# Test audio features endpoint
print("\n4️⃣  Testing audio features endpoint...")

try:
    # Get a track ID from search
    results = sp.search(q='happy', type='track', limit=1)
    track_id = results['tracks']['items'][0]['id']
    
    print(f"   Testing with track ID: {track_id}")
    
    # Try to get audio features
    features = sp.audio_features([track_id])
    
    if features and features[0]:
        print("   ✓ Audio features endpoint working!")
        print(f"   Valence: {features[0]['valence']:.2f}")
        print(f"   Energy: {features[0]['energy']:.2f}")
        
        print("\n" + "=" * 70)
        print("✅ ALL TESTS PASSED!")
        print("=" * 70)
        print("\nYour Spotify authentication is working correctly.")
        print("You can now run the data collector:")
        print("   python ultra_simple_collector.py")
        print("=" * 70)
        
    else:
        print("   ❌ Audio features returned None")
        print("\n⚠️  Authentication works, but audio features endpoint")
        print("   is returning empty data. This could be:")
        print("   1. Rate limiting (wait 30-60 minutes)")
        print("   2. Temporary API issue")
        print("\n💡 Solution: Use workaround_collector.py instead")
        
except Exception as e:
    error_str = str(e)
    
    if "403" in error_str:
        print(f"   ❌ 403 Forbidden Error")
        print("\n⚠️  Your authentication works, but you've hit rate limits.")
        print("\n💡 Solutions:")
        print("   1. Wait 30-60 minutes and try again")
        print("   2. Use: python workaround_collector.py")
        print("   3. Create a new Spotify app with fresh credentials")
        
    elif "token" in error_str.lower():
        print(f"   ❌ Token Error: {e}")
        print("\n🔧 This means authentication failed.")
        print("   Check your credentials are correct.")
        
    else:
        print(f"   ❌ Error: {e}")
        print("\n🔧 Try:")
        print("   1. Wait a few minutes")
        print("   2. Check internet connection")
        print("   3. Use workaround_collector.py")

print("\n" + "=" * 70)
