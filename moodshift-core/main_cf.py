"""
MoodShift with Collaborative Filtering Integration
Main system that combines mood-based and CF-enhanced playlist generation
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import argparse


class MoodShiftCF:
    """
    MoodShift with Collaborative Filtering integration.
    Creates mood-transitioning playlists with improved musical cohesion.
    """
    
    def __init__(self, dataset_path: str, verbose: bool = True):
        """
        Initialize MoodShift with CF.
        
        Args:
            dataset_path: Path to music dataset CSV
            verbose: Print initialization messages
        """
        self.verbose = verbose
        
        if self.verbose:
            print("🎵 Initializing MoodShift with CF...")
        
        # Load dataset
        if self.verbose:
            print(f"📂 Loading dataset from {dataset_path}...")
        self.dataset = pd.read_csv(dataset_path)
        
        if self.verbose:
            print(f"✓ Loaded {len(self.dataset)} tracks")
        
        # Initialize components
        if self.verbose:
            print("🔧 Initializing components...")
        
        # Import here to avoid circular imports
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
        
        from mood_classifier import MoodClassifier
        from collaborative_filtering import CollaborativeFilter
        from path_generator_cf import PathGeneratorCF
        
        self.mood_classifier = MoodClassifier()
        
        # Add mood classifications if needed
        if 'mood' not in self.dataset.columns:
            if self.verbose:
                print("   Adding mood classifications...")
            self.dataset = self.mood_classifier.classify_dataset(self.dataset)
        
        # Initialize CF (this builds similarity matrix)
        self.cf = CollaborativeFilter(self.dataset, verbose=self.verbose)
        
        # Initialize path generator with CF
        self.path_generator = PathGeneratorCF(
            self.dataset,
            self.mood_classifier,
            self.cf
        )
        
        if self.verbose:
            print("✅ MoodShift with CF ready!\n")
    
    def create_playlist(self, 
                       current_mood: str,
                       target_mood: str,
                       length: int = 10,
                       method: str = 'cf_enhanced',
                       cf_weight: float = 0.4,
                       smoothness: float = 0.7) -> pd.DataFrame:
        """
        Create a mood-transitioning playlist.
        
        Args:
            current_mood: Starting mood
            target_mood: Target mood
            length: Number of songs
            method: 'smooth' (original) or 'cf_enhanced' (with CF)
            cf_weight: Weight for CF (0-1), only used if method='cf_enhanced'
            smoothness: Smoothness parameter (0-1)
            
        Returns:
            DataFrame with playlist
        """
        valid_moods = ['happy_energetic', 'happy_calm', 'sad_calm', 
                      'sad_energetic', 'neutral']
        
        if current_mood not in valid_moods:
            raise ValueError(f"Invalid current_mood. Must be one of: {valid_moods}")
        if target_mood not in valid_moods:
            raise ValueError(f"Invalid target_mood. Must be one of: {valid_moods}")
        
        if self.verbose:
            print("=" * 70)
            print(f"Creating playlist: {current_mood} → {target_mood}")
            print(f"Method: {method}, Length: {length}")
            if method == 'cf_enhanced':
                print(f"CF weight: {cf_weight}")
            print("=" * 70)
        
        # Generate path
        if method == 'cf_enhanced':
            path = self.path_generator.generate_path_cf_enhanced(
                start_mood=current_mood,
                target_mood=target_mood,
                length=length,
                smoothness=smoothness,
                cf_weight=cf_weight,
                verbose=self.verbose
            )
        else:  # smooth (original)
            path = self.path_generator.generate_path_smooth(
                start_mood=current_mood,
                target_mood=target_mood,
                length=length,
                smoothness=smoothness
            )
        
        # Convert to DataFrame
        playlist_df = pd.DataFrame(path)
        
        return playlist_df
    
    def get_similar_tracks(self, track_id: str, n: int = 10) -> pd.DataFrame:
        """
        Find tracks similar to a given track.
        
        Args:
            track_id: Track ID
            n: Number of similar tracks
            
        Returns:
            DataFrame with similar tracks
        """
        similar = self.cf.get_similar_tracks(track_id, n=n)
        return pd.DataFrame(similar)
    
    def calculate_playlist_metrics(self, playlist: pd.DataFrame) -> Dict:
        """
        Calculate metrics for a playlist.
        
        Args:
            playlist: Playlist DataFrame
            
        Returns:
            Dict with metrics
        """
        path = playlist.to_dict('records')
        return self.path_generator.calculate_path_metrics(path)
    
    def compare_methods(self,
                       current_mood: str,
                       target_mood: str,
                       length: int = 10) -> Dict:
        """
        Compare original vs CF-enhanced methods.
        
        Args:
            current_mood: Starting mood
            target_mood: Target mood  
            length: Playlist length
            
        Returns:
            Dict with comparison results
        """
        print("\n" + "=" * 70)
        print("COMPARING METHODS")
        print("=" * 70)
        
        # Generate with both methods
        print("\n📊 Generating playlists...")
        
        playlist_original = self.create_playlist(
            current_mood, target_mood, length,
            method='smooth'
        )
        
        playlist_cf = self.create_playlist(
            current_mood, target_mood, length,
            method='cf_enhanced',
            cf_weight=0.4
        )
        
        # Calculate metrics
        metrics_orig = self.calculate_playlist_metrics(playlist_original)
        metrics_cf = self.calculate_playlist_metrics(playlist_cf)
        
        # Calculate improvements
        smoothness_imp = (
            (metrics_orig['smoothness'] - metrics_cf['smoothness']) /
            metrics_orig['smoothness'] * 100
        )
        
        cohesion_imp = (
            (metrics_cf['cf_cohesion'] - metrics_orig['cf_cohesion']) /
            (metrics_orig['cf_cohesion'] + 0.001) * 100
        )
        
        # Print comparison
        print("\n📈 RESULTS:")
        print("\nSmootness (lower is better):")
        print(f"  Original:     {metrics_orig['smoothness']:.3f}")
        print(f"  CF-Enhanced:  {metrics_cf['smoothness']:.3f}")
        print(f"  Improvement:  {smoothness_imp:+.1f}%")
        
        print("\nMusical Cohesion (higher is better):")
        print(f"  Original:     {metrics_orig['cf_cohesion']:.3f}")
        print(f"  CF-Enhanced:  {metrics_cf['cf_cohesion']:.3f}")
        print(f"  Improvement:  {cohesion_imp:+.1f}%")
        
        return {
            'original': {
                'playlist': playlist_original,
                'metrics': metrics_orig
            },
            'cf_enhanced': {
                'playlist': playlist_cf,
                'metrics': metrics_cf
            },
            'improvements': {
                'smoothness': smoothness_imp,
                'cohesion': cohesion_imp
            }
        }
    
    def save_playlist(self, playlist: pd.DataFrame, filename: str):
        """Save playlist to CSV."""
        playlist.to_csv(filename, index=False)
        if self.verbose:
            print(f"\n💾 Playlist saved to: {filename}")
    
    def get_dataset_statistics(self) -> Dict:
        """Get statistics about the dataset."""
        stats = {
            'total_tracks': len(self.dataset),
            'mood_distribution': self.dataset['mood'].value_counts().to_dict(),
            'cf_stats': self.cf.get_statistics()
        }
        return stats


def main():
    """CLI interface for MoodShift with CF"""
    parser = argparse.ArgumentParser(
        description='MoodShift with Collaborative Filtering'
    )
    
    # Dataset
    parser.add_argument('--dataset', type=str,
                       default='data/processed/spotify_mood_dataset.csv',
                       help='Path to music dataset')
    
    # Playlist parameters
    parser.add_argument('--current-mood', type=str, default='sad_calm',
                       help='Current mood')
    parser.add_argument('--target-mood', type=str, default='happy_energetic',
                       help='Target mood')
    parser.add_argument('--length', type=int, default=10,
                       help='Playlist length')
    
    # Method selection
    parser.add_argument('--method', type=str, default='cf_enhanced',
                       choices=['smooth', 'cf_enhanced'],
                       help='Generation method')
    parser.add_argument('--cf-weight', type=float, default=0.4,
                       help='CF weight (0-1), for cf_enhanced method')
    
    # Actions
    parser.add_argument('--compare', action='store_true',
                       help='Compare original vs CF-enhanced')
    parser.add_argument('--output', type=str,
                       default='moodshift_playlist.csv',
                       help='Output filename')
    
    args = parser.parse_args()
    
    # Initialize
    try:
        ms = MoodShiftCF(args.dataset)
    except FileNotFoundError:
        print(f"❌ Error: Dataset not found at {args.dataset}")
        return
    except Exception as e:
        print(f"❌ Error initializing: {e}")
        return
    
    # Show dataset statistics
    print("📊 Dataset Statistics:")
    stats = ms.get_dataset_statistics()
    print(f"   Total tracks: {stats['total_tracks']}")
    print(f"   Mood distribution:")
    for mood, count in stats['mood_distribution'].items():
        print(f"      {mood}: {count}")
    
    # Compare mode
    if args.compare:
        results = ms.compare_methods(
            args.current_mood,
            args.target_mood,
            args.length
        )
        
        # Save both playlists
        ms.save_playlist(
            results['original']['playlist'],
            'playlist_original.csv'
        )
        ms.save_playlist(
            results['cf_enhanced']['playlist'],
            'playlist_cf_enhanced.csv'
        )
        
        print("\n" + "=" * 70)
        print("✅ Comparison complete!")
        print("=" * 70)
        return
    
    # Normal mode - create playlist
    playlist = ms.create_playlist(
        current_mood=args.current_mood,
        target_mood=args.target_mood,
        length=args.length,
        method=args.method,
        cf_weight=args.cf_weight
    )
    
    # Display playlist
    print("\n🎵 Generated Playlist:")
    print("=" * 70)
    for idx, track in playlist.iterrows():
        print(f"{track['step']:2d}. {track['name'][:45]:45s} - {track['artist'][:20]:20s}")
        print(f"    Mood: {track['mood']:20s} (V={track['valence']:.2f}, E={track['energy']:.2f})")
    
    # Calculate and show metrics
    if len(playlist) > 1:
        metrics = ms.calculate_playlist_metrics(playlist)
        print("\n📈 Playlist Metrics:")
        print(f"   Smoothness: {metrics['smoothness']:.3f} (lower is better)")
        print(f"   CF Cohesion: {metrics['cf_cohesion']:.3f} (higher is better)")
        print(f"   Variety: {metrics['variety']:.3f}")
    
    # Save playlist
    ms.save_playlist(playlist, args.output)
    
    print("\n" + "=" * 70)
    print("✅ MoodShift with CF complete!")
    print("=" * 70)
    
    if args.method == 'cf_enhanced':
        print("\n💡 Tip: Try different --cf-weight values (0.0 to 1.0)")
        print("   0.0 = pure mood-based (original)")
        print("   0.4 = balanced (recommended)")
        print("   0.8 = heavy CF influence")


if __name__ == "__main__":
    main()
