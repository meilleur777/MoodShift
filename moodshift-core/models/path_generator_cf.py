"""
CF-Enhanced Path Generator for MoodShift
Generates playlists using both mood-based and collaborative filtering
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Set, Optional


class PathGeneratorCF:
    """
    Enhanced path generator that combines mood-based transitions
    with collaborative filtering for better musical cohesion.
    """
    
    def __init__(self, dataset: pd.DataFrame, mood_classifier, 
                 collaborative_filter, max_mood_jump: float = 0.25):
        """
        Initialize CF-enhanced path generator.
        
        Args:
            dataset: DataFrame with tracks
            mood_classifier: MoodClassifier instance
            collaborative_filter: CollaborativeFilter instance  
            max_mood_jump: Maximum mood distance between consecutive songs
        """
        self.dataset = dataset.copy()
        self.classifier = mood_classifier
        self.cf = collaborative_filter
        self.max_mood_jump = max_mood_jump
        
        # Ensure mood column exists
        if 'mood' not in self.dataset.columns:
            self.dataset = self.classifier.classify_dataset(self.dataset)
    
    def calculate_distance(self, valence1: float, energy1: float,
                          valence2: float, energy2: float) -> float:
        """Calculate Euclidean distance in mood space."""
        return np.sqrt((valence1 - valence2)**2 + (energy1 - energy2)**2)
    
    def find_nearest_tracks(self, valence: float, energy: float, 
                           n: int = 50, exclude_ids: Optional[Set[str]] = None) -> pd.DataFrame:
        """
        Find tracks nearest to a mood point.
        
        Args:
            valence: Target valence
            energy: Target energy
            n: Number of tracks to return
            exclude_ids: Set of track IDs to exclude
            
        Returns:
            DataFrame of nearest tracks
        """
        df = self.dataset.copy()
        
        # Exclude already used tracks
        if exclude_ids:
            df = df[~df['track_id'].isin(exclude_ids)]
        
        # Calculate distances
        df['distance'] = df.apply(
            lambda row: self.calculate_distance(
                row['valence'], row['energy'], valence, energy
            ),
            axis=1
        )
        
        return df.nsmallest(n, 'distance')
    
    def _track_to_dict(self, track, step: int) -> Dict:
        """Convert track row to dictionary."""
        return {
            'track_id': track['track_id'],
            'name': track['name'],
            'artist': track['artist'],
            'valence': float(track['valence']),
            'energy': float(track['energy']),
            'mood': track['mood'],
            'step': step
        }
    
    def generate_path_smooth(self, start_mood: str, target_mood: str,
                            length: int = 10, smoothness: float = 0.7) -> List[Dict]:
        """
        Generate smooth path using original mood-based method.
        (For comparison with CF-enhanced method)
        
        Args:
            start_mood: Starting mood
            target_mood: Target mood
            length: Playlist length
            smoothness: Smoothness weight (0-1)
            
        Returns:
            List of tracks
        """
        start_v, start_e = self.classifier.get_mood_center(start_mood)
        target_v, target_e = self.classifier.get_mood_center(target_mood)
        
        path = []
        used_ids = set()
        
        # Find starting track
        candidates = self.find_nearest_tracks(start_v, start_e, n=10)
        if len(candidates) == 0:
            return []
        
        current_track = candidates.iloc[0]
        path.append(self._track_to_dict(current_track, 1))
        used_ids.add(current_track['track_id'])
        
        # Generate rest of path
        for i in range(1, length):
            curr_v, curr_e = path[-1]['valence'], path[-1]['energy']
            
            # Calculate ideal next position
            progress = i / (length - 1)
            ideal_v = start_v + (target_v - start_v) * progress
            ideal_e = start_e + (target_e - start_e) * progress
            
            # Find candidates
            candidates = self.find_nearest_tracks(
                ideal_v, ideal_e, n=50, exclude_ids=used_ids
            )
            
            if len(candidates) == 0:
                break
            
            # Score candidates (mood-only)
            best_score = float('inf')
            best_track = None
            
            for _, candidate in candidates.iterrows():
                # Smoothness: distance from current
                smooth_dist = self.calculate_distance(
                    curr_v, curr_e,
                    candidate['valence'], candidate['energy']
                )
                
                # Progress: distance from ideal
                progress_dist = self.calculate_distance(
                    ideal_v, ideal_e,
                    candidate['valence'], candidate['energy']
                )
                
                # Combined (mood-only)
                score = smoothness * smooth_dist + (1 - smoothness) * progress_dist
                
                if score < best_score:
                    best_score = score
                    best_track = candidate
            
            if best_track is None:
                break
            
            path.append(self._track_to_dict(best_track, i + 1))
            used_ids.add(best_track['track_id'])
        
        return path
    
    def generate_path_cf_enhanced(self, start_mood: str, target_mood: str,
                                  length: int = 10, 
                                  smoothness: float = 0.7,
                                  cf_weight: float = 0.4,
                                  verbose: bool = False) -> List[Dict]:
        """
        Generate path using BOTH mood-based and CF similarity.
        
        This is the main CF-enhanced method!
        
        Args:
            start_mood: Starting mood
            target_mood: Target mood
            length: Playlist length
            smoothness: Mood smoothness weight (0-1)
            cf_weight: Collaborative filtering weight (0-1)
                      0 = pure mood-based (original)
                      1 = pure CF-based
                      0.4 = balanced (recommended)
            verbose: Print progress
            
        Returns:
            List of tracks with smooth mood + musical transitions
        """
        start_v, start_e = self.classifier.get_mood_center(start_mood)
        target_v, target_e = self.classifier.get_mood_center(target_mood)
        
        if verbose:
            print(f"\n🎵 Generating CF-enhanced path: {start_mood} → {target_mood}")
            print(f"   CF weight: {cf_weight:.1f} (0=mood only, 1=CF only)")
            print(f"   Smoothness: {smoothness:.1f}")
        
        path = []
        used_ids = set()
        
        # Find starting track
        candidates = self.find_nearest_tracks(start_v, start_e, n=10)
        if len(candidates) == 0:
            return []
        
        current_track = candidates.iloc[0]
        path.append(self._track_to_dict(current_track, 1))
        used_ids.add(current_track['track_id'])
        
        if verbose:
            print(f"   Start: {current_track['name'][:40]}")
        
        # Generate rest of path with CF
        for i in range(1, length):
            curr_v, curr_e = path[-1]['valence'], path[-1]['energy']
            current_track_id = path[-1]['track_id']
            
            # Calculate ideal next position
            progress = i / (length - 1)
            ideal_v = start_v + (target_v - start_v) * progress
            ideal_e = start_e + (target_e - start_e) * progress
            
            # Get CF-similar tracks to current
            cf_similar = self.cf.get_similar_tracks(
                current_track_id, 
                n=100,
                exclude_ids=used_ids
            )
            
            # Create lookup for CF similarities
            cf_dict = {t['track_id']: t['similarity'] for t in cf_similar}
            
            # Get mood-based candidates
            mood_candidates = self.find_nearest_tracks(
                ideal_v, ideal_e, n=50, exclude_ids=used_ids
            )
            
            if len(mood_candidates) == 0:
                break
            
            # Score candidates using BOTH mood and CF
            best_score = float('inf')
            best_track = None
            
            for _, candidate in mood_candidates.iterrows():
                # 1. Mood component
                smooth_dist = self.calculate_distance(
                    curr_v, curr_e,
                    candidate['valence'], candidate['energy']
                )
                
                progress_dist = self.calculate_distance(
                    ideal_v, ideal_e,
                    candidate['valence'], candidate['energy']
                )
                
                mood_score = smoothness * smooth_dist + (1 - smoothness) * progress_dist
                
                # 2. CF component
                cf_similarity = cf_dict.get(candidate['track_id'], 0)
                cf_score = 1 - cf_similarity  # Convert to distance
                
                # 3. COMBINE scores (this is the key!)
                final_score = (1 - cf_weight) * mood_score + cf_weight * cf_score
                
                if final_score < best_score:
                    best_score = final_score
                    best_track = candidate
            
            if best_track is None:
                break
            
            path.append(self._track_to_dict(best_track, i + 1))
            used_ids.add(best_track['track_id'])
            
            if verbose:
                cf_marker = "✨" if best_track['track_id'] in cf_dict else "  "
                print(f"   [{i+1:2d}] {cf_marker} {best_track['name'][:38]:38s} "
                      f"(V={best_track['valence']:.2f}, E={best_track['energy']:.2f})")
        
        return path
    
    def calculate_path_smoothness(self, path: List[Dict]) -> float:
        """
        Calculate smoothness metric for a path.
        
        Args:
            path: List of tracks
            
        Returns:
            Average mood distance between consecutive tracks (lower is better)
        """
        if len(path) < 2:
            return 0.0
        
        distances = []
        for i in range(len(path) - 1):
            dist = self.calculate_distance(
                path[i]['valence'], path[i]['energy'],
                path[i+1]['valence'], path[i+1]['energy']
            )
            distances.append(dist)
        
        return np.mean(distances)
    
    def calculate_path_metrics(self, path: List[Dict]) -> Dict:
        """
        Calculate comprehensive metrics for a path.
        
        Args:
            path: List of tracks
            
        Returns:
            Dict with metrics
        """
        if len(path) < 2:
            return {}
        
        # Smoothness
        smoothness = self.calculate_path_smoothness(path)
        
        # CF cohesion (average similarity between consecutive tracks)
        cf_similarities = []
        for i in range(len(path) - 1):
            sim = self.cf.get_similarity_score(
                path[i]['track_id'],
                path[i+1]['track_id']
            )
            cf_similarities.append(sim)
        cf_cohesion = np.mean(cf_similarities) if cf_similarities else 0
        
        # Variety
        valence_std = np.std([t['valence'] for t in path])
        energy_std = np.std([t['energy'] for t in path])
        variety = (valence_std + energy_std) / 2
        
        # Progression (are we moving toward target consistently?)
        # This would need target coordinates - simplified here
        progression = 1.0 - smoothness  # Rough estimate
        
        return {
            'smoothness': smoothness,
            'cf_cohesion': cf_cohesion,
            'variety': variety,
            'progression': progression,
            'length': len(path)
        }


def main():
    """Example usage and comparison"""
    import os
    import sys
    
    # Add parent directory to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    try:
        from models.mood_classifier import MoodClassifier
        from models.collaborative_filtering import CollaborativeFilter
    except ImportError:
        print("❌ Required modules not found!")
        print("Make sure mood_classifier.py and collaborative_filtering.py are in models/")
        return
    
    # Load dataset
    data_path = '../data/processed/spotify_mood_dataset.csv'
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        return
    
    print("=" * 70)
    print("CF-ENHANCED PATH GENERATOR - Testing")
    print("=" * 70)
    
    # Load and initialize
    print("\n📂 Loading components...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} tracks")
    
    classifier = MoodClassifier()
    cf = CollaborativeFilter(df, verbose=False)
    path_gen = PathGeneratorCF(df, classifier, cf)
    
    # Test 1: Original smooth method
    print("\n" + "=" * 70)
    print("TEST 1: Original Smooth Method")
    print("=" * 70)
    
    path_original = path_gen.generate_path_smooth(
        'sad_calm', 'happy_energetic', length=8
    )
    
    print(f"\nGenerated {len(path_original)} tracks")
    for track in path_original[:3]:
        print(f"  • {track['name'][:40]}")
    print("  ...")
    
    metrics_orig = path_gen.calculate_path_metrics(path_original)
    print(f"\nMetrics:")
    print(f"  Smoothness: {metrics_orig['smoothness']:.3f}")
    print(f"  CF Cohesion: {metrics_orig['cf_cohesion']:.3f}")
    
    # Test 2: CF-enhanced method
    print("\n" + "=" * 70)
    print("TEST 2: CF-Enhanced Method")
    print("=" * 70)
    
    path_cf = path_gen.generate_path_cf_enhanced(
        'sad_calm', 'happy_energetic', 
        length=8, cf_weight=0.4, verbose=True
    )
    
    metrics_cf = path_gen.calculate_path_metrics(path_cf)
    print(f"\nMetrics:")
    print(f"  Smoothness: {metrics_cf['smoothness']:.3f}")
    print(f"  CF Cohesion: {metrics_cf['cf_cohesion']:.3f}")
    
    # Comparison
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)
    
    smoothness_improvement = (
        (metrics_orig['smoothness'] - metrics_cf['smoothness']) / 
        metrics_orig['smoothness'] * 100
    )
    cohesion_improvement = (
        (metrics_cf['cf_cohesion'] - metrics_orig['cf_cohesion']) / 
        (metrics_orig['cf_cohesion'] + 0.001) * 100
    )
    
    print(f"\nSmootness:")
    print(f"  Original: {metrics_orig['smoothness']:.3f}")
    print(f"  CF-Enhanced: {metrics_cf['smoothness']:.3f}")
    print(f"  Improvement: {smoothness_improvement:+.1f}%")
    
    print(f"\nCF Cohesion:")
    print(f"  Original: {metrics_orig['cf_cohesion']:.3f}")
    print(f"  CF-Enhanced: {metrics_cf['cf_cohesion']:.3f}")
    print(f"  Improvement: {cohesion_improvement:+.1f}%")
    
    print("\n" + "=" * 70)
    print("✅ CF-enhanced path generation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
