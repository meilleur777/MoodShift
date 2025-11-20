"""
Path Generator for MoodShift
Generates playlists that smoothly transition from current mood to target mood
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
    Generates smooth mood transition paths using A* pathfinding algorithm.
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
    
    def generate_path_greedy(self, start_mood: str, target_mood: str, 
                            length: int = 10) -> List[Dict]:
        """
        Generate a path using greedy algorithm (simple, fast).
        
        Args:
            start_mood: Starting mood category
            target_mood: Target mood category
            length: Number of songs in playlist
            
        Returns:
            List of track dictionaries forming the path
        """
        # Get start and end points
        start_valence, start_energy = self.classifier.get_mood_center(start_mood)
        target_valence, target_energy = self.classifier.get_mood_center(target_mood)
        
        # Initialize path
        path = []
        used_ids = set()
        
        # Current position
        current_valence = start_valence
        current_energy = start_energy
        
        # Calculate step size
        valence_step = (target_valence - start_valence) / (length - 1)
        energy_step = (target_energy - start_energy) / (length - 1)
        
        print(f"\n🎵 Generating path: {start_mood} → {target_mood}")
        print(f"   Start: (V={start_valence:.2f}, E={start_energy:.2f})")
        print(f"   Target: (V={target_valence:.2f}, E={target_energy:.2f})")
        print(f"   Steps: {length} songs\n")
        
        for i in range(length):
            # Find nearest track to current position
            candidates = self.find_nearest_tracks(
                current_valence, current_energy,
                n=20,
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
                  f"(V={track['valence']:.2f}, E={track['energy']:.2f})")
            
            # Move to next target position
            current_valence += valence_step
            current_energy += energy_step
        
        return path
    
    def generate_path_smooth(self, start_mood: str, target_mood: str,
                            length: int = 10, smoothness: float = 0.7) -> List[Dict]:
        """
        Generate a smooth path with minimal jumps between songs.
        
        Args:
            start_mood: Starting mood category
            target_mood: Target mood category
            length: Number of songs in playlist
            smoothness: Weight for smoothness vs. direct path (0-1)
            
        Returns:
            List of track dictionaries forming the path
        """
        start_valence, start_energy = self.classifier.get_mood_center(start_mood)
        target_valence, target_energy = self.classifier.get_mood_center(target_mood)
        
        path = []
        used_ids = set()
        
        # Start with a track near the starting mood
        candidates = self.find_nearest_tracks(start_valence, start_energy, n=10)
        if len(candidates) == 0:
            return []
        
        current_track = candidates.iloc[0]
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
        
        print(f"\n🎵 Generating smooth path: {start_mood} → {target_mood}")
        print(f"   Start: {current_track['name'][:40]}")
        
        for i in range(1, length):
            # Current position
            curr_v = path[-1]['valence']
            curr_e = path[-1]['energy']
            
            # Ideal next position (toward target)
            progress = i / (length - 1)
            ideal_v = start_valence + (target_valence - start_valence) * progress
            ideal_e = start_energy + (target_energy - start_energy) * progress
            
            # Find candidates
            candidates = self.find_nearest_tracks(curr_v, curr_e, n=50, exclude_ids=used_ids)
            
            if len(candidates) == 0:
                break
            
            # Score candidates based on smoothness and progress toward target
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
                
                # Combined score
                score = smoothness * smooth_dist + (1 - smoothness) * progress_dist
                
                if score < best_score:
                    best_score = score
                    best_track = candidate
            
            if best_track is None:
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
            
            print(f"   [{i+1:2d}] {best_track['name'][:40]:40s} "
                  f"(V={best_track['valence']:.2f}, E={best_track['energy']:.2f})")
        
        # Calculate smoothness metric
        smoothness_score = self.calculate_path_smoothness(path)
        print(f"\n   ✓ Path smoothness: {smoothness_score:.3f} (lower is better)")
        
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
    """Example usage of PathGenerator"""
    import os
    
    # Load dataset
    data_path = '../data/processed/spotify_mood_dataset.csv'
    
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        print(f"Expected: {data_path}")
        return
    
    print("=" * 70)
    print("PATH GENERATOR - Example Usage")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} tracks")
    
    # Initialize path generator
    generator = PathGenerator(df)
    
    # Example 1: Greedy path
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Greedy Path (Fast)")
    print("=" * 70)
    
    path1 = generator.generate_path_greedy(
        start_mood='sad_calm',
        target_mood='happy_energetic',
        length=10
    )
    
    # Example 2: Smooth path
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Smooth Path (Better transitions)")
    print("=" * 70)
    
    path2 = generator.generate_path_smooth(
        start_mood='sad_calm',
        target_mood='happy_energetic',
        length=10,
        smoothness=0.7
    )
    
    # Save playlist
    generator.save_playlist(path2, 'moodshift_playlist.csv')
    
    print("\n" + "=" * 70)
    print("✅ Path generation complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
