"""
CF-Enhanced Path Generator with Randomization
Adds variety through probabilistic selection and serendipity
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Set, Optional


class PathGeneratorCFRandom:
    """
    Enhanced path generator with randomization options.
    Creates varied playlists even with same inputs!
    """
    
    def __init__(self, dataset: pd.DataFrame, mood_classifier, 
                 collaborative_filter, max_mood_jump: float = 0.25,
                 random_seed: Optional[int] = None):
        """
        Initialize CF-enhanced path generator with randomization.
        
        Args:
            dataset: DataFrame with tracks
            mood_classifier: MoodClassifier instance
            collaborative_filter: CollaborativeFilter instance  
            max_mood_jump: Maximum mood distance between consecutive songs
            random_seed: Random seed for reproducibility (None = random)
        """
        self.dataset = dataset.copy()
        self.classifier = mood_classifier
        self.cf = collaborative_filter
        self.max_mood_jump = max_mood_jump
        
        # Set random seed if provided
        if random_seed is not None:
            np.random.seed(random_seed)
        
        # Ensure mood column exists
        if 'mood' not in self.dataset.columns:
            self.dataset = self.classifier.classify_dataset(self.dataset)
    
    def calculate_distance(self, valence1: float, energy1: float,
                          valence2: float, energy2: float) -> float:
        """Calculate Euclidean distance in mood space."""
        return np.sqrt((valence1 - valence2)**2 + (energy1 - energy2)**2)
    
    def find_nearest_tracks(self, valence: float, energy: float, 
                           n: int = 50, exclude_ids: Optional[Set[str]] = None) -> pd.DataFrame:
        """Find tracks nearest to a mood point."""
        df = self.dataset.copy()
        
        if exclude_ids:
            df = df[~df['track_id'].isin(exclude_ids)]
        
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
    
    def _select_with_randomness(self, candidates: pd.DataFrame, scores: np.ndarray,
                                randomness: float = 0.0) -> pd.Series:
        """
        Select track from candidates with randomness.
        
        Args:
            candidates: DataFrame of candidate tracks
            scores: Array of scores (lower is better)
            randomness: Randomness level (0-1)
                       0.0 = Always pick best
                       0.5 = Pick from top 10
                       1.0 = Completely random
        
        Returns:
            Selected track
        """
        if randomness == 0:
            # Deterministic: always pick best
            best_idx = np.argmin(scores)
            return candidates.iloc[best_idx]
        
        # Add small random noise to scores based on randomness
        noise_scale = randomness * np.std(scores) if len(scores) > 1 else randomness
        noisy_scores = scores + np.random.normal(0, noise_scale, len(scores))
        
        # Temperature-based selection (higher randomness = higher temperature)
        temperature = 1.0 + randomness * 4.0  # 1.0 to 5.0
        
        # Convert scores to probabilities (lower score = higher probability)
        # Use softmax with temperature
        exp_scores = np.exp(-noisy_scores / temperature)
        probabilities = exp_scores / np.sum(exp_scores)
        
        # Sample based on probabilities
        selected_idx = np.random.choice(len(candidates), p=probabilities)
        
        return candidates.iloc[selected_idx]
    
    def generate_path_smooth(self, start_mood: str, target_mood: str,
                            length: int = 10, smoothness: float = 0.7,
                            randomness: float = 0.0,
                            verbose: bool = False) -> List[Dict]:
        """
        Generate smooth path with optional randomness.
        
        Args:
            start_mood: Starting mood
            target_mood: Target mood
            length: Playlist length
            smoothness: Smoothness weight (0-1)
            randomness: Randomness level (0-1)
            verbose: Print progress
            
        Returns:
            List of tracks
        """
        start_v, start_e = self.classifier.get_mood_center(start_mood)
        target_v, target_e = self.classifier.get_mood_center(target_mood)
        
        path = []
        used_ids = set()
        
        # Find starting track (with randomness)
        candidates = self.find_nearest_tracks(start_v, start_e, n=20)
        if len(candidates) == 0:
            return []
        
        if randomness > 0:
            # Randomize starting track selection
            scores = candidates['distance'].values
            current_track = self._select_with_randomness(candidates, scores, randomness)
        else:
            current_track = candidates.iloc[0]
        
        path.append(self._track_to_dict(current_track, 1))
        used_ids.add(current_track['track_id'])
        
        # Generate rest of path
        for i in range(1, length):
            curr_v, curr_e = path[-1]['valence'], path[-1]['energy']
            
            progress = i / (length - 1)
            ideal_v = start_v + (target_v - start_v) * progress
            ideal_e = start_e + (target_e - start_e) * progress
            
            candidates = self.find_nearest_tracks(
                ideal_v, ideal_e, n=50, exclude_ids=used_ids
            )
            
            if len(candidates) == 0:
                break
            
            # Score candidates
            scores = []
            for _, candidate in candidates.iterrows():
                smooth_dist = self.calculate_distance(
                    curr_v, curr_e,
                    candidate['valence'], candidate['energy']
                )
                
                progress_dist = self.calculate_distance(
                    ideal_v, ideal_e,
                    candidate['valence'], candidate['energy']
                )
                
                score = smoothness * smooth_dist + (1 - smoothness) * progress_dist
                scores.append(score)
            
            scores = np.array(scores)
            
            # Select with randomness
            best_track = self._select_with_randomness(candidates, scores, randomness)
            
            if best_track is None:
                break
            
            path.append(self._track_to_dict(best_track, i + 1))
            used_ids.add(best_track['track_id'])
        
        return path
    
    def generate_path_cf_enhanced(self, start_mood: str, target_mood: str,
                                  length: int = 10, 
                                  smoothness: float = 0.7,
                                  cf_weight: float = 0.4,
                                  randomness: float = 0.0,
                                  diversity_weight: float = 0.0,
                                  serendipity: bool = False,
                                  verbose: bool = False) -> List[Dict]:
        """
        Generate path using CF with randomization options.
        
        Args:
            start_mood: Starting mood
            target_mood: Target mood
            length: Playlist length
            smoothness: Mood smoothness weight (0-1)
            cf_weight: Collaborative filtering weight (0-1)
            randomness: How random to be (0-1)
            diversity_weight: Avoid very similar tracks (0-1)
            serendipity: Enable unexpected discoveries
            verbose: Print progress
            
        Returns:
            List of tracks with variety!
        """
        start_v, start_e = self.classifier.get_mood_center(start_mood)
        target_v, target_e = self.classifier.get_mood_center(target_mood)
        
        if verbose:
            print(f"\n🎵 Generating CF-enhanced path: {start_mood} → {target_mood}")
            print(f"   CF weight: {cf_weight:.1f}, Randomness: {randomness:.1f}")
            if diversity_weight > 0:
                print(f"   Diversity: {diversity_weight:.1f}")
            if serendipity:
                print(f"   ✨ Serendipity: ON")
        
        path = []
        used_ids = set()
        
        # Find starting track (with randomness)
        candidates = self.find_nearest_tracks(start_v, start_e, n=20)
        if len(candidates) == 0:
            return []
        
        if randomness > 0:
            scores = candidates['distance'].values
            current_track = self._select_with_randomness(candidates, scores, randomness)
        else:
            current_track = candidates.iloc[0]
        
        path.append(self._track_to_dict(current_track, 1))
        used_ids.add(current_track['track_id'])
        
        if verbose:
            print(f"   Start: {current_track['name'][:40]}")
        
        # Generate rest of path with CF + randomization
        for i in range(1, length):
            curr_v, curr_e = path[-1]['valence'], path[-1]['energy']
            current_track_id = path[-1]['track_id']
            
            progress = i / (length - 1)
            ideal_v = start_v + (target_v - start_v) * progress
            ideal_e = start_e + (target_e - start_e) * progress
            
            # Get CF-similar tracks
            cf_similar = self.cf.get_similar_tracks(
                current_track_id, 
                n=100,
                exclude_ids=used_ids
            )
            
            cf_dict = {t['track_id']: t['similarity'] for t in cf_similar}
            
            # Get mood-based candidates (get more for randomness)
            n_candidates = 100 if randomness > 0 else 50
            mood_candidates = self.find_nearest_tracks(
                ideal_v, ideal_e, n=n_candidates, exclude_ids=used_ids
            )
            
            if len(mood_candidates) == 0:
                break
            
            # Score candidates
            scores = []
            for _, candidate in mood_candidates.iterrows():
                # Mood component
                smooth_dist = self.calculate_distance(
                    curr_v, curr_e,
                    candidate['valence'], candidate['energy']
                )
                
                progress_dist = self.calculate_distance(
                    ideal_v, ideal_e,
                    candidate['valence'], candidate['energy']
                )
                
                mood_score = smoothness * smooth_dist + (1 - smoothness) * progress_dist
                
                # CF component
                cf_similarity = cf_dict.get(candidate['track_id'], 0)
                cf_score = 1 - cf_similarity
                
                # Diversity penalty (if enabled)
                diversity_penalty = 0
                if diversity_weight > 0 and len(path) >= 2:
                    # Check similarity to recent tracks
                    recent_sims = []
                    for prev_track in path[-2:]:
                        prev_id = prev_track['track_id']
                        if prev_id in self.cf.track_id_to_idx and candidate['track_id'] in self.cf.track_id_to_idx:
                            sim = self.cf.get_similarity_score(prev_id, candidate['track_id'])
                            recent_sims.append(sim)
                    
                    if recent_sims:
                        # High similarity to recent = penalty
                        diversity_penalty = diversity_weight * np.mean(recent_sims)
                
                # Serendipity bonus (if enabled)
                serendipity_bonus = 0
                if serendipity:
                    # Occasionally favor slightly unexpected tracks
                    # Tracks that are good but not top-scored
                    if np.random.random() < 0.15:  # 15% chance
                        serendipity_bonus = -0.1  # Small bonus (lower score = better)
                
                # Combined score
                final_score = (
                    (1 - cf_weight) * mood_score + 
                    cf_weight * cf_score +
                    diversity_penalty +
                    serendipity_bonus
                )
                
                scores.append(final_score)
            
            scores = np.array(scores)
            
            # Select with randomness
            best_track = self._select_with_randomness(mood_candidates, scores, randomness)
            
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
        """Calculate smoothness metric for a path."""
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
        """Calculate comprehensive metrics for a path."""
        if len(path) < 2:
            return {}
        
        # Smoothness
        smoothness = self.calculate_path_smoothness(path)
        
        # CF cohesion
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
        
        # Progression
        progression = 1.0 - smoothness
        
        return {
            'smoothness': smoothness,
            'cf_cohesion': cf_cohesion,
            'variety': variety,
            'progression': progression,
            'length': len(path)
        }


def main():
    """Example usage with randomization"""
    import os
    import sys
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    
    try:
        from models.mood_classifier import MoodClassifier
        from models.collaborative_filtering import CollaborativeFilter
    except ImportError:
        print("❌ Required modules not found!")
        return
    
    data_path = '../data/processed/spotify_mood_dataset.csv'
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        return
    
    print("=" * 70)
    print("CF-ENHANCED PATH GENERATOR WITH RANDOMIZATION - Testing")
    print("=" * 70)
    
    df = pd.read_csv(data_path)
    classifier = MoodClassifier()
    cf = CollaborativeFilter(df, verbose=False)
    path_gen = PathGeneratorCFRandom(df, classifier, cf)
    
    # Test randomness levels
    print("\n" + "=" * 70)
    print("COMPARING RANDOMNESS LEVELS")
    print("=" * 70)
    
    for randomness in [0.0, 0.3, 0.7]:
        print(f"\n🎲 Randomness: {randomness}")
        
        path = path_gen.generate_path_cf_enhanced(
            'sad_calm', 'happy_energetic', 
            length=5, cf_weight=0.4, 
            randomness=randomness,
            verbose=False
        )
        
        print(f"   Tracks: {', '.join([t['name'][:20] for t in path])}")
        
        metrics = path_gen.calculate_path_metrics(path)
        print(f"   Smoothness: {metrics['smoothness']:.3f}")
        print(f"   CF Cohesion: {metrics['cf_cohesion']:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Run this multiple times to see variation!")
    print("=" * 70)


if __name__ == "__main__":
    main()
