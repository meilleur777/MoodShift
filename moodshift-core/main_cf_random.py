"""
MoodShift with Collaborative Filtering - Enhanced with Randomization
Adds variety through randomized selection and serendipity options
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import argparse


class MoodShiftCF:
    """
    MoodShift with Collaborative Filtering integration.
    Creates mood-transitioning playlists with improved musical cohesion.
    NOW WITH RANDOMIZATION for varied results!
    """
    
    def __init__(self, dataset_path: str, verbose: bool = True, random_seed: Optional[int] = None):
        """
        Initialize MoodShift with CF.
        
        Args:
            dataset_path: Path to music dataset CSV
            verbose: Print initialization messages
            random_seed: Random seed for reproducibility (None = random every time)
        """
        self.verbose = verbose
        self.random_seed = random_seed
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
            if self.verbose:
                print(f"🎲 Random seed set to: {random_seed}")
        
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
        from path_generator_cf_random import PathGeneratorCFRandom
        
        self.mood_classifier = MoodClassifier()
        
        # Add mood classifications if needed
        if 'mood' not in self.dataset.columns:
            if self.verbose:
                print("   Adding mood classifications...")
            self.dataset = self.mood_classifier.classify_dataset(self.dataset)
        
        # Initialize CF (this builds similarity matrix)
        self.cf = CollaborativeFilter(self.dataset, verbose=self.verbose)
        
        # Initialize path generator with CF and randomization
        self.path_generator = PathGeneratorCFRandom(
            self.dataset,
            self.mood_classifier,
            self.cf,
            random_seed=random_seed
        )
        
        if self.verbose:
            print("✅ MoodShift with CF ready!\n")
    
    def create_playlist(self, 
                       current_mood: str,
                       target_mood: str,
                       length: int = 10,
                       method: str = 'cf_enhanced',
                       cf_weight: float = 0.4,
                       smoothness: float = 0.7,
                       randomness: float = 0.0,
                       diversity_weight: float = 0.0,
                       serendipity: bool = False) -> pd.DataFrame:
        """
        Create a mood-transitioning playlist with randomization options.
        
        Args:
            current_mood: Starting mood
            target_mood: Target mood
            length: Number of songs
            method: 'smooth' (original) or 'cf_enhanced' (with CF)
            cf_weight: Weight for CF (0-1), only used if method='cf_enhanced'
            smoothness: Smoothness parameter (0-1)
            randomness: How random to be (0-1)
                       0.0 = Always pick best (deterministic)
                       0.3 = Sometimes pick from top 5
                       0.5 = Often pick from top 10
                       0.7 = Usually pick from top 20
                       1.0 = Completely random from candidates
            diversity_weight: Avoid very similar consecutive tracks (0-1)
                             0.0 = No diversity enforcement
                             0.5 = Moderate diversity
                             1.0 = Maximum diversity
            serendipity: Enable "happy accidents" (unexpected good tracks)
            
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
            if randomness > 0:
                print(f"🎲 Randomness: {randomness}")
            if diversity_weight > 0:
                print(f"🌈 Diversity: {diversity_weight}")
            if serendipity:
                print(f"✨ Serendipity: ON")
            print("=" * 70)
        
        # Generate path with randomization
        if method == 'cf_enhanced':
            path = self.path_generator.generate_path_cf_enhanced(
                start_mood=current_mood,
                target_mood=target_mood,
                length=length,
                smoothness=smoothness,
                cf_weight=cf_weight,
                randomness=randomness,
                diversity_weight=diversity_weight,
                serendipity=serendipity,
                verbose=self.verbose
            )
        else:  # smooth (original)
            path = self.path_generator.generate_path_smooth(
                start_mood=current_mood,
                target_mood=target_mood,
                length=length,
                smoothness=smoothness,
                randomness=randomness,
                verbose=self.verbose
            )
        
        # Convert to DataFrame
        playlist_df = pd.DataFrame(path)
        
        return playlist_df
    
    def get_similar_tracks(self, track_id: str, n: int = 10) -> pd.DataFrame:
        """Find tracks similar to a given track."""
        similar = self.cf.get_similar_tracks(track_id, n=n)
        return pd.DataFrame(similar)
    
    def calculate_playlist_metrics(self, playlist: pd.DataFrame) -> Dict:
        """Calculate metrics for a playlist."""
        path = playlist.to_dict('records')
        return self.path_generator.calculate_path_metrics(path)
    
    def compare_randomness_levels(self,
                                  current_mood: str,
                                  target_mood: str,
                                  length: int = 10) -> Dict:
        """
        Compare playlists with different randomness levels.
        
        Args:
            current_mood: Starting mood
            target_mood: Target mood  
            length: Playlist length
            
        Returns:
            Dict with comparison results
        """
        print("\n" + "=" * 70)
        print("COMPARING RANDOMNESS LEVELS")
        print("=" * 70)
        
        randomness_levels = [
            (0.0, "Deterministic (always same)"),
            (0.3, "Low randomness"),
            (0.5, "Medium randomness"),
            (0.7, "High randomness")
        ]
        
        results = {}
        
        for randomness, description in randomness_levels:
            print(f"\n🎲 Testing: {description} (randomness={randomness})")
            
            playlist = self.create_playlist(
                current_mood, target_mood, length,
                method='cf_enhanced',
                cf_weight=0.4,
                randomness=randomness
            )
            
            metrics = self.calculate_playlist_metrics(playlist)
            
            results[randomness] = {
                'description': description,
                'playlist': playlist,
                'metrics': metrics
            }
            
            print(f"   Smoothness: {metrics['smoothness']:.3f}")
            print(f"   CF Cohesion: {metrics['cf_cohesion']:.3f}")
            print(f"   First 3 tracks: {', '.join(playlist['name'].head(3))}")
        
        return results
    
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
    """CLI interface for MoodShift with CF and Randomization"""
    parser = argparse.ArgumentParser(
        description='MoodShift with Collaborative Filtering and Randomization'
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
    
    # Randomization options (NEW!)
    parser.add_argument('--randomness', type=float, default=0.0,
                       help='Randomness level (0-1). 0=deterministic, 1=random')
    parser.add_argument('--diversity', type=float, default=0.0,
                       help='Diversity weight (0-1). Higher = more diverse')
    parser.add_argument('--serendipity', action='store_true',
                       help='Enable serendipity (unexpected discoveries)')
    parser.add_argument('--seed', type=int, default=None,
                       help='Random seed for reproducibility')
    
    # Actions
    parser.add_argument('--compare-randomness', action='store_true',
                       help='Compare different randomness levels')
    parser.add_argument('--output', type=str,
                       default='moodshift_playlist.csv',
                       help='Output filename')
    
    args = parser.parse_args()
    
    # Initialize
    try:
        ms = MoodShiftCF(args.dataset, random_seed=args.seed)
    except FileNotFoundError:
        print(f"❌ Error: Dataset not found at {args.dataset}")
        print("\nOptions:")
        print("1. Generate sample data: python generate_sample_dataset.py")
        print("2. Specify your dataset: --dataset /path/to/your/data.csv")
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
    
    # Compare randomness mode
    if args.compare_randomness:
        results = ms.compare_randomness_levels(
            args.current_mood,
            args.target_mood,
            args.length
        )
        
        print("\n" + "=" * 70)
        print("✅ Randomness comparison complete!")
        print("=" * 70)
        print("\n💡 Run multiple times to see variation in random modes")
        return
    
    # Normal mode - create playlist with randomization
    playlist = ms.create_playlist(
        current_mood=args.current_mood,
        target_mood=args.target_mood,
        length=args.length,
        method=args.method,
        cf_weight=args.cf_weight,
        randomness=args.randomness,
        diversity_weight=args.diversity,
        serendipity=args.serendipity
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
    
    if args.randomness > 0:
        print("\n🎲 Tip: Run again to get a different playlist!")
        print(f"   Current randomness: {args.randomness}")
        print("   Try: --randomness 0.0 (deterministic)")
        print("        --randomness 0.3 (slight variation)")
        print("        --randomness 0.7 (high variation)")
    else:
        print("\n💡 Tip: Add --randomness 0.5 for varied results!")
        print("   Or try --diversity 0.5 for more diverse playlists")
        print("   Or add --serendipity for unexpected discoveries")


if __name__ == "__main__":
    main()
