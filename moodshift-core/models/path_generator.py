"""
Path Generator for MoodShift (ENHANCED VERSION)
Added starting_intensity parameter for better first song selection

NEW FEATURE: Control how intense/emotional the starting song should be
- 'gentle': Start with the calmest song in the mood zone
- 'moderate': Start with moderate intensity (default)
- 'intense': Start with more emotional/powerful song
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import heapq
from dataclasses import dataclass
from mood_classifier import MoodClassifier


@dataclass
class PathNode:
    """Represents a track in the path"""
    track_id: str
    valence: float
    energy: float
    distance_to_target: float
    total_distance: float
    
    def __lt__(self, other):
        return self.total_distance < other.total_distance


class PathGenerator:
    """
    Generates smooth mood transition paths.
    Creates playlists that gradually shift from current mood to target mood.
    """
    
    def __init__(self, dataset: pd.DataFrame, max_mood_jump: float = 0.25):
        """
        Initialize path generator.
        
        Args:
            dataset: DataFrame with tracks and audio features
            max_mood_jump: Maximum allowed mood distance between consecutive songs
        """
        self.dataset = dataset.copy()
        self.classifier = MoodClassifier()
        self.max_mood_jump = max_mood_jump
        
        # Add mood classifications if not present
        if 'mood' not in self.dataset.columns:
            self.dataset = self.classifier.classify_dataset(self.dataset)
    
    def calculate_distance(self, valence1: float, energy1: float,
                          valence2: float, energy2: float) -> float:
        """Calculate Euclidean distance in mood space."""
        return np.sqrt((valence1 - valence2)**2 + (energy1 - energy2)**2)
    
    def calculate_intensity(self, valence: float, energy: float) -> float:
        """
        Calculate emotional intensity of a track.
        
        Intensity considers:
        - Distance from center (0.5, 0.5) - more extreme = more intense
        - Energy level - higher energy = more intense
        
        Returns:
            Intensity score (0-1, higher = more intense)
        """
        # Distance from neutral center
        distance_from_center = np.sqrt((valence - 0.5)**2 + (energy - 0.5)**2)
        
        # Weight: 60% distance from center, 40% energy level
        intensity = 0.6 * (distance_from_center / 0.707) + 0.4 * energy
        
        return intensity
    
    def find_starting_track(self, start_mood: str, intensity: str = 'moderate') -> Dict:
        """
        Find an appropriate starting track based on mood and desired intensity.
        
        Args:
            start_mood: Starting mood category
            intensity: 'gentle', 'moderate', or 'intense'
            
        Returns:
            Track dictionary
        """
        start_valence, start_energy = self.classifier.get_mood_center(start_mood)
        
        # Get tracks in the starting mood
        mood_tracks = self.dataset[self.dataset['mood'] == start_mood].copy()
        
        if len(mood_tracks) == 0:
            # Fallback: find closest tracks to mood center
            mood_tracks = self.find_nearest_tracks(start_valence, start_energy, n=20)
        
        # Calculate intensity for each track
        mood_tracks['intensity'] = mood_tracks.apply(
            lambda row: self.calculate_intensity(row['valence'], row['energy']),
            axis=1
        )
        
        # Select based on intensity preference
        if intensity == 'gentle':
            # Choose calmest track (lowest intensity)
            selected = mood_tracks.nsmallest(5, 'intensity').sample(1).iloc[0]
            print(f"   Starting with GENTLE intensity: {selected['intensity']:.3f}")
        elif intensity == 'intense':
            # Choose most powerful track (highest intensity)
            selected = mood_tracks.nlargest(5, 'intensity').sample(1).iloc[0]
            print(f"   Starting with INTENSE intensity: {selected['intensity']:.3f}")
        else:  # moderate
            # Choose middle intensity
            median_intensity = mood_tracks['intensity'].median()
            mood_tracks['intensity_diff'] = abs(mood_tracks['intensity'] - median_intensity)
            selected = mood_tracks.nsmallest(5, 'intensity_diff').sample(1).iloc[0]
            print(f"   Starting with MODERATE intensity: {selected['intensity']:.3f}")
        
        return selected
    
    def find_nearest_tracks(self, valence: float, energy: float, 
                           n: int = 50, exclude_ids: set = None) -> pd.DataFrame:
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
    
    def find_candidates_for_transition(self, current_v: float, current_e: float,
                                      target_v: float, target_e: float,
                                      progress: float, n: int = 50,
                                      exclude_ids: set = None) -> pd.DataFrame:
        """
        Find candidates in the direction of target, not just near current position.
        
        Args:
            current_v, current_e: Current position
            target_v, target_e: Target position
            progress: How far along the path (0-1)
            n: Number of candidates
            exclude_ids: Tracks to exclude
            
        Returns:
            DataFrame of candidate tracks
        """
        # Calculate search position - move toward target
        search_factor = 0.3 + 0.3 * progress
        
        search_v = current_v + search_factor * (target_v - current_v)
        search_e = current_e + search_factor * (target_e - current_e)
        
        candidates = self.find_nearest_tracks(search_v, search_e, n=n, exclude_ids=exclude_ids)
        
        # Fallback strategy - if all candidates are too far, expand search
        if len(candidates) > 0 and candidates.iloc[0]['distance'] > 0.3:
            ideal_v = current_v + (target_v - current_v) / 10
            ideal_e = current_e + (target_e - current_e) / 10
            candidates = self.find_nearest_tracks(ideal_v, ideal_e, n=n*2, exclude_ids=exclude_ids)
        
        return candidates
    
    def generate_path_greedy(self, start_mood: str, target_mood: str, 
                            length: int = 10, 
                            starting_intensity: str = 'moderate') -> List[Dict]:
        """
        Generate a path using greedy algorithm (simple, fast).
        
        Args:
            start_mood: Starting mood category
            target_mood: Target mood category
            length: Number of songs in playlist
            starting_intensity: 'gentle', 'moderate', or 'intense' for first song
            
        Returns:
            List of track dictionaries forming the path
        """
        # Get start and end points
        start_valence, start_energy = self.classifier.get_mood_center(start_mood)
        target_valence, target_energy = self.classifier.get_mood_center(target_mood)
        
        # Initialize path
        path = []
        used_ids = set()
        
        print(f"\n🎵 Generating path: {start_mood} → {target_mood}")
        print(f"   Start: (V={start_valence:.2f}, E={start_energy:.2f})")
        print(f"   Target: (V={target_valence:.2f}, E={target_energy:.2f})")
        print(f"   Steps: {length} songs")
        print(f"   Starting intensity: {starting_intensity}\n")
        
        # Find starting track with appropriate intensity
        current_track = self.find_starting_track(start_mood, starting_intensity)
        
        path.append({
            'track_id': current_track['track_id'],
            'name': current_track['name'],
            'artist': current_track['artist'],
            'valence': current_track['valence'],
            'energy': current_track['energy'],
            'mood': current_track['mood'],
            'step': 1
        })
        used_ids.add(current_track['track_id'])
        
        print(f"   [1] {current_track['name'][:40]:40s} "
              f"(V={current_track['valence']:.2f}, E={current_track['energy']:.2f}) "
              f"mood: {current_track['mood']}")
        
        # Current position starts at actual track position
        current_valence = current_track['valence']
        current_energy = current_track['energy']
        
        for i in range(1, length):
            progress = i / (length - 1) if length > 1 else 1.0
            
            # Find candidates using improved search
            candidates = self.find_candidates_for_transition(
                current_valence, current_energy,
                target_valence, target_energy,
                progress=progress,
                n=50,
                exclude_ids=used_ids
            )
            
            if len(candidates) == 0:
                print(f"   ⚠️  Step {i+1}: No more tracks available")
                break
            
            # Select best candidate
            track = candidates.iloc[0]
            
            # Add to path
            path.append({
                'track_id': track['track_id'],
                'name': track['name'],
                'artist': track['artist'],
                'valence': track['valence'],
                'energy': track['energy'],
                'mood': track['mood'],
                'step': i + 1
            })
            
            used_ids.add(track['track_id'])
            
            print(f"   [{i+1:2d}] {track['name'][:40]:40s} "
                  f"(V={track['valence']:.2f}, E={track['energy']:.2f}) "
                  f"mood: {track['mood']}")
            
            # Update current position
            current_valence = track['valence']
            current_energy = track['energy']
        
        return path
    
    def generate_path_smooth(self, start_mood: str, target_mood: str,
                            length: int = 10, smoothness: float = 0.7,
                            starting_intensity: str = 'moderate') -> List[Dict]:
        """
        Generate a smooth path with minimal jumps between songs.
        
        Args:
            start_mood: Starting mood category
            target_mood: Target mood category
            length: Number of songs in playlist
            smoothness: Initial weight for smoothness vs. direct path (0-1)
            starting_intensity: 'gentle', 'moderate', or 'intense' for first song
            
        Returns:
            List of track dictionaries forming the path
        """
        start_valence, start_energy = self.classifier.get_mood_center(start_mood)
        target_valence, target_energy = self.classifier.get_mood_center(target_mood)
        
        path = []
        used_ids = set()
        
        print(f"\n🎵 Generating smooth path: {start_mood} → {target_mood}")
        print(f"   Starting intensity: {starting_intensity}")
        
        # Find starting track with appropriate intensity
        current_track = self.find_starting_track(start_mood, starting_intensity)
        
        path.append({
            'track_id': current_track['track_id'],
            'name': current_track['name'],
            'artist': current_track['artist'],
            'valence': current_track['valence'],
            'energy': current_track['energy'],
            'mood': current_track['mood'],
            'step': 1
        })
        used_ids.add(current_track['track_id'])
        
        print(f"   [{1:2d}] {current_track['name'][:40]:40s} "
              f"(V={current_track['valence']:.2f}, E={current_track['energy']:.2f}) "
              f"mood: {current_track['mood']}")
        
        for i in range(1, length):
            # Current position
            curr_v = path[-1]['valence']
            curr_e = path[-1]['energy']
            
            # Progress through the path
            progress = i / (length - 1)
            
            # Ideal next position (toward target)
            ideal_v = start_valence + (target_valence - start_valence) * progress
            ideal_e = start_energy + (target_energy - start_energy) * progress
            
            # Find candidates using improved search
            candidates = self.find_candidates_for_transition(
                curr_v, curr_e,
                target_valence, target_energy,
                progress=progress,
                n=100,
                exclude_ids=used_ids
            )
            
            if len(candidates) == 0:
                print(f"   ⚠️  Step {i+1}: No more tracks available")
                break
            
            # Dynamic scoring - increase progress weight as we advance
            smoothness_weight = smoothness * (1 - progress * 0.6)
            progress_weight = 1 - smoothness_weight
            
            # Score candidates
            best_score = float('inf')
            best_track = None
            
            for idx, candidate in candidates.iterrows():
                # Distance from current track (smoothness)
                smooth_dist = self.calculate_distance(
                    curr_v, curr_e,
                    candidate['valence'], candidate['energy']
                )
                
                # Distance from ideal position (progress toward target)
                progress_dist = self.calculate_distance(
                    ideal_v, ideal_e,
                    candidate['valence'], candidate['energy']
                )
                
                # Combined score with dynamic weighting
                score = smoothness_weight * smooth_dist + progress_weight * progress_dist
                
                if score < best_score:
                    best_score = score
                    best_track = candidate
            
            if best_track is None:
                print(f"   ⚠️  Step {i+1}: No suitable track found")
                break
            
            path.append({
                'track_id': best_track['track_id'],
                'name': best_track['name'],
                'artist': best_track['artist'],
                'valence': best_track['valence'],
                'energy': best_track['energy'],
                'mood': best_track['mood'],
                'step': i + 1
            })
            used_ids.add(best_track['track_id'])
            
            # Show transition info
            mood_dist = self.calculate_distance(curr_v, curr_e, 
                                               best_track['valence'], best_track['energy'])
            print(f"   [{i+1:2d}] {best_track['name'][:40]:40s} "
                  f"(V={best_track['valence']:.2f}, E={best_track['energy']:.2f}) "
                  f"mood: {best_track['mood']:20s} jump: {mood_dist:.3f}")
        
        # Calculate smoothness metric
        smoothness_score = self.calculate_path_smoothness(path)
        print(f"\n   ✓ Path smoothness: {smoothness_score:.3f} (lower is better)")
        
        # Check if we reached target
        if len(path) > 0:
            final_dist = self.calculate_distance(
                path[-1]['valence'], path[-1]['energy'],
                target_valence, target_energy
            )
            print(f"   ✓ Distance to target: {final_dist:.3f}")
        
        return path
    
    def calculate_path_smoothness(self, path: List[Dict]) -> float:
        """
        Calculate average mood distance between consecutive songs.
        
        Args:
            path: List of tracks in the path
            
        Returns:
            Average distance between consecutive tracks
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
    
    def save_playlist(self, path: List[Dict], filename: str):
        """
        Save playlist to CSV file.
        
        Args:
            path: List of tracks
            filename: Output filename
        """
        df = pd.DataFrame(path)
        df.to_csv(filename, index=False)
        print(f"\n💾 Playlist saved to: {filename}")


def main():
    """Example usage of PathGenerator with starting_intensity"""
    import os
    
    # Load dataset
    data_path = '../data/processed/spotify_mood_dataset.csv'
    
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        return
    
    print("=" * 70)
    print("PATH GENERATOR - WITH STARTING INTENSITY CONTROL")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} tracks")
    
    # Initialize path generator
    generator = PathGenerator(df)
    
    # Example 1: Gentle start (less intense first song)
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Gentle Start")
    print("=" * 70)
    
    path1 = generator.generate_path_smooth(
        start_mood='sad_calm',
        target_mood='happy_energetic',
        length=10,
        smoothness=0.7,
        starting_intensity='gentle'  # ← NEW PARAMETER
    )
    
    if len(path1) > 0:
        generator.save_playlist(path1, 'playlist_gentle_start.csv')
    
    # Example 2: Moderate start (default)
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Moderate Start (Default)")
    print("=" * 70)
    
    path2 = generator.generate_path_smooth(
        start_mood='sad_calm',
        target_mood='happy_energetic',
        length=10,
        smoothness=0.7,
        starting_intensity='moderate'
    )
    
    # Example 3: Intense start (powerful first song)
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Intense Start")
    print("=" * 70)
    
    path3 = generator.generate_path_smooth(
        start_mood='sad_calm',
        target_mood='happy_energetic',
        length=10,
        smoothness=0.7,
        starting_intensity='intense'
    )
    
    print("\n" + "=" * 70)
    print("✅ Examples complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
