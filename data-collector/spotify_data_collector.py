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
        
        # Process in batches of 100
        for i in range(0, len(track_ids), 100):
            batch = track_ids[i:i+100]
            features = self.sp.audio_features(batch)
            
            # Filter out None results
            all_features.extend([f for f in features if f is not None])
            
            # Be nice to the API
            time.sleep(0.1)
        
        return all_features
    
    def search_tracks_by_mood(self, mood_params: Dict, limit: int = 50) -> List[Dict]:
        """
        Search for tracks based on mood parameters using Spotify's recommendation system
        
        Args:
            mood_params: Dictionary with audio feature targets (valence, energy, etc.)
            limit: Number of tracks to retrieve
            
        Returns:
            List of track dictionaries
        """
        # Get seed tracks (popular tracks)
        seed_tracks = []
        results = self.sp.search(q='year:2020-2024', type='track', limit=5)
        for track in results['tracks']['items']:
            seed_tracks.append(track['id'])
        
        # Get recommendations based on mood parameters
        recommendations = self.sp.recommendations(
            seed_tracks=seed_tracks[:5],  # Max 5 seed tracks
            limit=limit,
            **mood_params
        )
        
        tracks = []
        for track in recommendations['tracks']:
            tracks.append({
                'track_id': track['id'],
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'popularity': track['popularity'],
                'duration_ms': track['duration_ms']
            })
        
        return tracks
    
    def collect_diverse_dataset(self, num_tracks_per_category: int = 100) -> pd.DataFrame:
        """
        Collect a diverse dataset covering different moods
        
        Args:
            num_tracks_per_category: Number of tracks to collect per mood category
            
        Returns:
            DataFrame with tracks and their features
        """
        # Define mood categories based on valence and energy
        mood_categories = {
            'happy_energetic': {'target_valence': 0.8, 'target_energy': 0.8},
            'happy_calm': {'target_valence': 0.8, 'target_energy': 0.3},
            'sad_energetic': {'target_valence': 0.2, 'target_energy': 0.8},
            'sad_calm': {'target_valence': 0.2, 'target_energy': 0.3},
            'neutral': {'target_valence': 0.5, 'target_energy': 0.5}
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
    # You need to get these from https://developer.spotify.com/dashboard
    CLIENT_ID = "your_client_id_here"
    CLIENT_SECRET = "your_client_secret_here"
    
    # Initialize collector
    collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
    
    # Method 1: Collect diverse dataset based on mood categories
    print("=" * 60)
    print("Method 1: Collecting diverse dataset")
    print("=" * 60)
    df_diverse = collector.collect_diverse_dataset(num_tracks_per_category=100)
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
