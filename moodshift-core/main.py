"""
MoodShift - Main Recommendation System
Combines mood classification, collaborative filtering, and path generation
to create mood-transitioning playlists
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import sys
import os

# Add models to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))

from mood_classifier import MoodClassifier
from path_generator import PathGenerator
from collaborative_filtering import CollaborativeFilter


class MoodShift:
    """
    Main MoodShift recommendation system.
    Creates personalized playlists that transition between mood states.
    """
    
    def __init__(self, dataset_path: str):
        """
        Initialize MoodShift system.
        
        Args:
            dataset_path: Path to the music dataset CSV
        """
        print("🎵 Initializing MoodShift...")
        
        # Load dataset
        print(f"📂 Loading dataset from {dataset_path}...")
        self.dataset = pd.read_csv(dataset_path)
        print(f"✓ Loaded {len(self.dataset)} tracks")
        
        # Initialize components
        print("🔧 Initializing components...")
        self.mood_classifier = MoodClassifier()
        
        # Ensure dataset has mood column
        if 'mood' not in self.dataset.columns and 'mood_category' not in self.dataset.columns:
            print("   Adding mood classifications...")
            self.dataset = self.mood_classifier.classify_dataset(self.dataset)
        elif 'mood_category' in self.dataset.columns and 'mood' not in self.dataset.columns:
            # Rename mood_category to mood for consistency
            self.dataset['mood'] = self.dataset['mood_category']
        
        self.path_generator = PathGenerator(self.dataset)
        self.collaborative_filter = CollaborativeFilter(self.dataset)
        
        print("✅ MoodShift ready!\n")
    
    def create_playlist(self, current_mood: str, target_mood: str,
                       length: int = 10, method: str = 'smooth',
                       use_collaborative: bool = False) -> pd.DataFrame:
        """
        Create a mood-transitioning playlist.
        
        Args:
            current_mood: Starting mood (happy_energetic, sad_calm, etc.)
            target_mood: Desired target mood
            length: Number of songs in playlist
            method: 'greedy' or 'smooth' path generation
            use_collaborative: Whether to use collaborative filtering
            
        Returns:
            DataFrame with playlist tracks
        """
        print("=" * 70)
        print(f"Creating playlist: {current_mood} → {target_mood}")
        print("=" * 70)
        
        # Validate moods
        valid_moods = ['happy_energetic', 'happy_calm', 'sad_calm', 
                      'sad_energetic', 'neutral']
        
        if current_mood not in valid_moods:
            raise ValueError(f"Invalid current_mood. Must be one of: {valid_moods}")
        if target_mood not in valid_moods:
            raise ValueError(f"Invalid target_mood. Must be one of: {valid_moods}")
        
        # Generate path
        if method == 'smooth':
            path = self.path_generator.generate_path_smooth(
                start_mood=current_mood,
                target_mood=target_mood,
                length=length
            )
        else:
            path = self.path_generator.generate_path_greedy(
                start_mood=current_mood,
                target_mood=target_mood,
                length=length
            )
        
        # Convert to DataFrame
        playlist_df = pd.DataFrame(path)
        
        # Add recommendations using collaborative filtering
        if use_collaborative and len(path) > 0:
            print("\n🎯 Enhancing with collaborative filtering...")
            # Replace some tracks with similar but potentially better ones
            for i in range(min(3, len(path))):  # Enhance first 3 tracks
                track_id = path[i]['track_id']
                similar = self.collaborative_filter.get_similar_tracks(
                    track_id, n=3,
                    exclude_ids={t['track_id'] for t in path}
                )
                if similar:
                    print(f"   Alternative for track {i+1}: {similar[0]['name']}")
        
        return playlist_df
    
    def get_mood_recommendations(self, mood: str, n: int = 10) -> pd.DataFrame:
        """
        Get top tracks for a specific mood.
        
        Args:
            mood: Mood category
            n: Number of tracks to return
            
        Returns:
            DataFrame with recommended tracks
        """
        # Get center of mood
        valence, energy = self.mood_classifier.get_mood_center(mood)
        
        # Find closest tracks
        tracks = self.mood_classifier.find_closest_tracks(
            self.dataset, valence, energy, n=n
        )
        
        return tracks[['track_id', 'name', 'artist', 'valence', 'energy', 'distance']]
    
    def analyze_track(self, track_id: str) -> Dict:
        """
        Analyze a track's mood characteristics.
        
        Args:
            track_id: Track ID
            
        Returns:
            Dictionary with track analysis
        """
        track = self.dataset[self.dataset['track_id'] == track_id]
        
        if len(track) == 0:
            return {'error': 'Track not found'}
        
        track = track.iloc[0]
        
        # Classify mood
        mood = self.mood_classifier.classify(
            track['valence'], track['energy']
        )
        
        # Find similar tracks
        similar = self.collaborative_filter.get_similar_tracks(track_id, n=5)
        
        return {
            'track_id': track_id,
            'name': track['name'],
            'artist': track['artist'],
            'valence': track['valence'],
            'energy': track['energy'],
            'mood': mood,
            'similar_tracks': [s['name'] for s in similar]
        }
    
    def get_dataset_statistics(self) -> Dict:
        """Get statistics about the dataset."""
        # Check if mood column exists, if not use mood_category
        mood_col = 'mood' if 'mood' in self.dataset.columns else 'mood_category'
        
        stats = {
            'total_tracks': len(self.dataset),
            'mood_distribution': self.dataset[mood_col].value_counts().to_dict() if mood_col in self.dataset.columns else {},
            'valence_stats': {
                'mean': self.dataset['valence'].mean(),
                'std': self.dataset['valence'].std(),
                'min': self.dataset['valence'].min(),
                'max': self.dataset['valence'].max()
            },
            'energy_stats': {
                'mean': self.dataset['energy'].mean(),
                'std': self.dataset['energy'].std(),
                'min': self.dataset['energy'].min(),
                'max': self.dataset['energy'].max()
            }
        }
        return stats
    
    def save_playlist(self, playlist: pd.DataFrame, filename: str):
        """Save playlist to file."""
        playlist.to_csv(filename, index=False)
        print(f"\n💾 Playlist saved to: {filename}")


def main():
    """Example usage of MoodShift system"""
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='MoodShift - Mood-based Music Recommendations')
    parser.add_argument('--dataset', type=str, 
                       default='../data/processed/spotify_mood_dataset.csv',
                       help='Path to music dataset')
    parser.add_argument('--current-mood', type=str, default='sad_calm',
                       help='Current mood (sad_calm, happy_energetic, etc.)')
    parser.add_argument('--target-mood', type=str, default='happy_energetic',
                       help='Target mood')
    parser.add_argument('--length', type=int, default=10,
                       help='Playlist length')
    parser.add_argument('--method', type=str, default='smooth',
                       choices=['smooth', 'greedy'],
                       help='Path generation method')
    parser.add_argument('--output', type=str, default='moodshift_playlist.csv',
                       help='Output filename')
    
    args = parser.parse_args()
    
    # Initialize MoodShift
    try:
        moodshift = MoodShift(args.dataset)
    except FileNotFoundError:
        print(f"❌ Error: Dataset not found at {args.dataset}")
        print("\nPlease run the data collector first to create the dataset.")
        return
    
    # Show dataset statistics
    print("📊 Dataset Statistics:")
    stats = moodshift.get_dataset_statistics()
    print(f"   Total tracks: {stats['total_tracks']}")
    print(f"   Mood distribution:")
    for mood, count in stats['mood_distribution'].items():
        print(f"      {mood}: {count} tracks")
    
    # Create playlist
    print("\n" + "=" * 70)
    playlist = moodshift.create_playlist(
        current_mood=args.current_mood,
        target_mood=args.target_mood,
        length=args.length,
        method=args.method
    )
    
    # Display playlist
    print("\n🎵 Generated Playlist:")
    print("=" * 70)
    for idx, track in playlist.iterrows():
        print(f"{track['step']:2d}. {track['name'][:45]:45s} - {track['artist'][:25]:25s}")
        print(f"    Mood: {track['mood']:20s} (V={track['valence']:.2f}, E={track['energy']:.2f})")
    
    # Calculate and display metrics
    if len(playlist) > 1:
        smoothness = moodshift.path_generator.calculate_path_smoothness(
            playlist.to_dict('records')
        )
        print("\n📈 Playlist Metrics:")
        print(f"   Smoothness score: {smoothness:.3f} (lower is better)")
        print(f"   Start mood: {playlist.iloc[0]['mood']}")
        print(f"   End mood: {playlist.iloc[-1]['mood']}")
    
    # Save playlist
    moodshift.save_playlist(playlist, args.output)
    
    print("\n" + "=" * 70)
    print("✅ MoodShift complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Listen to the playlist in order")
    print("  2. Notice how the mood gradually shifts")
    print("  3. Adjust parameters for different experiences")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
