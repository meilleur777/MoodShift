"""
MoodShift - Spotify Data Collector
Collects track data and audio features from Spotify API for mood-based recommendation system
"""

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time
from typing import List, Dict
import json
import os
from pathlib import Path

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class SpotifyDataCollector:
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Spotify API client
        
        Args:
            client_id: Spotify API client ID
            client_secret: Spotify API client secret
        """
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
        )
    
    def get_playlist_tracks(self, playlist_id: str) -> List[Dict]:
        """
        Get all tracks from a playlist
        
        Args:
            playlist_id: Spotify playlist ID or URI
            
        Returns:
            List of track dictionaries
        """
        tracks = []
        results = self.sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track']:  # Sometimes tracks can be None
                    track = item['track']
                    tracks.append({
                        'track_id': track['id'],
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'popularity': track['popularity'],
                        'duration_ms': track['duration_ms']
                    })
            
            # Get next page if available
            if results['next']:
                results = self.sp.next(results)
            else:
                results = None
                
        return tracks
    
    def get_audio_features(self, track_ids: List[str]) -> List[Dict]:
        """
        Get audio features for multiple tracks
        Spotify allows up to 100 tracks per request
        
        Args:
            track_ids: List of Spotify track IDs
            
        Returns:
            List of audio feature dictionaries
        """
        all_features = []
        
        # Process in batches of 50 to be safe (API says 100 max, but let's be conservative)
        batch_size = 50
        total_batches = (len(track_ids) + batch_size - 1) // batch_size
        
        print(f"  Processing {len(track_ids)} tracks in {total_batches} batches...")
        
        for i in range(0, len(track_ids), batch_size):
            batch = track_ids[i:i+batch_size]
            batch_num = (i // batch_size) + 1
            
            try:
                print(f"  [{batch_num}/{total_batches}] Fetching features for {len(batch)} tracks...", end=' ')
                features = self.sp.audio_features(batch)
                
                if features:
                    # Filter out None results
                    valid_features = [f for f in features if f is not None]
                    all_features.extend(valid_features)
                    print(f"✓ Got {len(valid_features)} features")
                else:
                    print("⚠️  No features returned")
                
            except Exception as e:
                print(f"⚠️  Error: {str(e)[:50]}")
                # Try one by one for this batch if batch fails
                print(f"    Retrying tracks individually...")
                for track_id in batch:
                    try:
                        feature = self.sp.audio_features([track_id])
                        if feature and feature[0]:
                            all_features.append(feature[0])
                    except:
                        continue  # Skip this track if it fails
            
            # Be nice to the API
            time.sleep(0.2)
        
        print(f"  Total features collected: {len(all_features)}")
        return all_features
    
    def search_tracks_by_mood(self, mood_params: Dict, limit: int = 50) -> List[Dict]:
        """
        Search for tracks based on mood parameters using Spotify's recommendation system
        
        Args:
            mood_params: Dictionary with audio feature min/max values (valence, energy, etc.)
            limit: Number of tracks to retrieve (will be fetched in batches)
            
        Returns:
            List of track dictionaries
        """
        # Spotify recommendations API works best with genres
        # Popular genres that work well for mood-based recommendations
        seed_genres = ['pop', 'rock', 'indie', 'electronic', 'hip-hop']
        
        tracks = []
        max_per_request = 50
        
        # Calculate how many batches we need
        num_batches = (limit + max_per_request - 1) // max_per_request
        
        for batch_num in range(num_batches):
            try:
                # How many more tracks do we need?
                remaining = limit - len(tracks)
                batch_limit = min(remaining, max_per_request)
                
                # Rotate through genres for variety
                genre_set = seed_genres[batch_num % len(seed_genres):]
                
                # Get recommendations based on mood parameters
                # Use min/max parameters which are better supported
                recommendations = self.sp.recommendations(
                    seed_genres=genre_set[:3],  # Use 3 genres for variety
                    limit=batch_limit,
                    **mood_params
                )
                
                # Extract track info
                if recommendations and 'tracks' in recommendations:
                    for track in recommendations['tracks']:
                        if track:  # Make sure track is not None
                            tracks.append({
                                'track_id': track['id'],
                                'name': track['name'],
                                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                                'album': track['album']['name'],
                                'popularity': track['popularity'],
                                'duration_ms': track['duration_ms']
                            })
                
                # Stop if we have enough tracks
                if len(tracks) >= limit:
                    break
                    
                # Rate limiting between batches
                time.sleep(0.3)
                
            except Exception as e:
                print(f"    Warning: Error in batch {batch_num + 1}: {str(e)}")
                # Try with a simpler approach using just one genre
                try:
                    simple_recommendations = self.sp.recommendations(
                        seed_genres=['pop'],
                        limit=min(20, remaining),
                        **mood_params
                    )
                    if simple_recommendations and 'tracks' in simple_recommendations:
                        for track in simple_recommendations['tracks']:
                            if track and len(tracks) < limit:
                                tracks.append({
                                    'track_id': track['id'],
                                    'name': track['name'],
                                    'artist': ', '.join([artist['name'] for artist in track['artists']]),
                                    'album': track['album']['name'],
                                    'popularity': track['popularity'],
                                    'duration_ms': track['duration_ms']
                                })
                except:
                    pass  # If even the simple approach fails, continue to next batch
                
                continue
        
        return tracks[:limit]  # Return exactly the requested number
    
    def collect_diverse_dataset(self, num_tracks_per_category: int = 50) -> pd.DataFrame:
        """
        Collect a diverse dataset covering different moods
        
        Args:
            num_tracks_per_category: Number of tracks to collect per mood category
                                    (default: 50, max recommended: 100)
            
        Returns:
            DataFrame with tracks and their features
        """
        # Define mood categories based on valence and energy
        # Using min/max ranges instead of target values for better API compatibility
        mood_categories = {
            'happy_energetic': {
                'min_valence': 0.6, 'max_valence': 1.0,
                'min_energy': 0.6, 'max_energy': 1.0
            },
            'happy_calm': {
                'min_valence': 0.6, 'max_valence': 1.0,
                'min_energy': 0.0, 'max_energy': 0.4
            },
            'sad_energetic': {
                'min_valence': 0.0, 'max_valence': 0.4,
                'min_energy': 0.6, 'max_energy': 1.0
            },
            'sad_calm': {
                'min_valence': 0.0, 'max_valence': 0.4,
                'min_energy': 0.0, 'max_energy': 0.4
            },
            'neutral': {
                'min_valence': 0.4, 'max_valence': 0.6,
                'min_energy': 0.4, 'max_energy': 0.6
            }
        }
        
        all_tracks = []
        
        print("Collecting tracks for different mood categories...")
        for mood_name, params in mood_categories.items():
            print(f"  Collecting {mood_name} tracks...")
            tracks = self.search_tracks_by_mood(params, limit=num_tracks_per_category)
            
            for track in tracks:
                track['mood_category'] = mood_name
            
            all_tracks.extend(tracks)
            time.sleep(0.5)  # Rate limiting
        
        # Remove duplicates
        track_ids = list(set([t['track_id'] for t in all_tracks]))
        print(f"\nCollected {len(track_ids)} unique tracks")
        
        # Get audio features
        print("Fetching audio features...")
        audio_features = self.get_audio_features(track_ids)
        
        # Create feature lookup
        features_dict = {f['id']: f for f in audio_features}
        
        # Combine track info with audio features
        combined_data = []
        for track in all_tracks:
            if track['track_id'] in features_dict:
                features = features_dict[track['track_id']]
                combined = {**track, **features}
                combined_data.append(combined)
        
        df = pd.DataFrame(combined_data)
        
        # Keep only relevant columns
        columns_to_keep = [
            'track_id', 'name', 'artist', 'album', 'popularity', 'duration_ms',
            'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo',
            'mood_category'
        ]
        
        df = df[columns_to_keep]
        
        return df
    
    def collect_from_playlists(self, playlist_ids: List[str]) -> pd.DataFrame:
        """
        Collect tracks from multiple playlists
        
        Args:
            playlist_ids: List of Spotify playlist IDs
            
        Returns:
            DataFrame with tracks and their features
        """
        all_tracks = []
        
        print(f"Collecting tracks from {len(playlist_ids)} playlists...")
        for idx, playlist_id in enumerate(playlist_ids):
            print(f"  Processing playlist {idx+1}/{len(playlist_ids)}...")
            tracks = self.get_playlist_tracks(playlist_id)
            all_tracks.extend(tracks)
            time.sleep(0.5)
        
        # Remove duplicates
        track_ids = list(set([t['track_id'] for t in all_tracks]))
        print(f"\nCollected {len(track_ids)} unique tracks")
        
        # Get audio features
        print("Fetching audio features...")
        audio_features = self.get_audio_features(track_ids)
        
        # Create feature lookup
        features_dict = {f['id']: f for f in audio_features}
        
        # Combine track info with audio features
        combined_data = []
        for track in all_tracks:
            if track['track_id'] in features_dict:
                features = features_dict[track['track_id']]
                combined = {**track, **features}
                combined_data.append(combined)
        
        df = pd.DataFrame(combined_data)
        
        # Keep only relevant columns
        columns_to_keep = [
            'track_id', 'name', 'artist', 'album', 'popularity', 'duration_ms',
            'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness',
            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo'
        ]
        
        df = df[[col for col in columns_to_keep if col in df.columns]]
        
        return df


def main():
    """
    Example usage of the SpotifyDataCollector
    """
    # Try to get credentials from environment variables first
    CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    # If not found in environment, use hardcoded values (for manual setup)
    if not CLIENT_ID or not CLIENT_SECRET:
        print("⚠️  No .env file found or credentials not set in environment variables")
        print("Using hardcoded credentials from this file...\n")
        
        # You can set your credentials here directly
        CLIENT_ID = "your_client_id_here"
        CLIENT_SECRET = "your_client_secret_here"
    else:
        print("✓ Loaded credentials from .env file\n")
    
    # Validate credentials
    if CLIENT_ID == "your_client_id_here" or CLIENT_SECRET == "your_client_secret_here":
        print("=" * 60)
        print("❌ ERROR: Spotify API credentials not configured!")
        print("=" * 60)
        print("\nOption 1 (Recommended): Use .env file")
        print("  1. Install python-dotenv: pip install python-dotenv")
        print("  2. Create a .env file in the same directory as this script")
        print("  3. Add these lines to .env:")
        print("     SPOTIFY_CLIENT_ID=your_client_id_here")
        print("     SPOTIFY_CLIENT_SECRET=your_client_secret_here")
        print("\nOption 2: Edit this file directly")
        print(f"  1. Open {__file__}")
        print("  2. Find the main() function (around line 250)")
        print("  3. Replace 'your_client_id_here' and 'your_client_secret_here'")
        print("\nTo get your credentials:")
        print("  → Visit https://developer.spotify.com/dashboard")
        print("  → Click on your app → Settings")
        print("  → Copy Client ID and Client Secret")
        print("=" * 60)
        return
    
    # Display credential info (safely)
    print(f"✓ Client ID: {CLIENT_ID[:10]}...{CLIENT_ID[-5:]}")
    print(f"✓ Client Secret configured (length: {len(CLIENT_SECRET)} chars)")
    
    try:
        # Initialize collector
        print("\n" + "=" * 60)
        print("Initializing Spotify API connection...")
        print("=" * 60)
        collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
        print("✓ Successfully connected to Spotify API!\n")
    except Exception as e:
        print(f"\n❌ Failed to connect to Spotify API: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify your Client ID and Client Secret are correct")
        print("  2. Make sure there are no extra spaces")
        print("  3. Check that your app is created on Spotify Dashboard")
        return
    
    # Method 1: Collect diverse dataset based on mood categories
    print("=" * 60)
    print("Method 1: Collecting diverse dataset")
    print("=" * 60)
    print("Collecting 50 tracks per mood category (5 categories)")
    print("This will result in ~250 unique tracks after deduplication")
    print("=" * 60)
    df_diverse = collector.collect_diverse_dataset(num_tracks_per_category=50)
    print(f"\nDataset shape: {df_diverse.shape}")
    print("\nFirst few rows:")
    print(df_diverse.head())
    
    # Save to CSV
    df_diverse.to_csv('spotify_mood_dataset.csv', index=False)
    print("\nDataset saved to 'spotify_mood_dataset.csv'")
    
    # Method 2: Collect from specific playlists (optional)
    # Example mood-based playlist IDs (you can replace with your own)
    """
    print("\n" + "=" * 60)
    print("Method 2: Collecting from playlists")
    print("=" * 60)
    
    playlist_ids = [
        '37i9dQZF1DX3rxVfibe1L0',  # Mood Booster
        '37i9dQZF1DX3YSRoSdA634',  # Chill Hits
        # Add more playlist IDs here
    ]
    
    df_playlists = collector.collect_from_playlists(playlist_ids)
    df_playlists.to_csv('spotify_playlist_dataset.csv', index=False)
    print("\nPlaylist dataset saved to 'spotify_playlist_dataset.csv'")
    """
    
    # Display dataset statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"Total tracks: {len(df_diverse)}")
    if 'mood_category' in df_diverse.columns:
        print("\nTracks per mood category:")
        print(df_diverse['mood_category'].value_counts())
    
    print("\nAudio features summary:")
    feature_cols = ['valence', 'energy', 'danceability', 'acousticness']
    print(df_diverse[feature_cols].describe())


if __name__ == "__main__":
    main()
