"""
Mood Classifier for MoodShift
Classifies songs into mood categories based on audio features (valence and energy)
Uses Russell's Circumplex Model of Affect
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler


class MoodClassifier:
    """
    Classifies songs into mood categories based on valence and energy.
    
    Mood Space (Russell's Circumplex Model):
        Energy
          ↑
      1.0 |  Tense/Angry  |  Happy/Energetic
          |               |
      0.5 |----------Neutral-----------
          |               |
      0.0 |   Sad/Calm    |  Peaceful/Content
          |_______________|_____________→ Valence
         0.0             0.5           1.0
    """
    
    def __init__(self, valence_threshold: float = 0.5, energy_threshold: float = 0.5):
        """
        Initialize mood classifier.
        
        Args:
            valence_threshold: Boundary between low/high valence (default: 0.5)
            energy_threshold: Boundary between low/high energy (default: 0.5)
        """
        self.valence_threshold = valence_threshold
        self.energy_threshold = energy_threshold
        
        # Mood definitions
        self.mood_definitions = {
            'happy_energetic': {
                'valence_min': 0.6, 'valence_max': 1.0,
                'energy_min': 0.6, 'energy_max': 1.0,
                'description': 'Upbeat, exciting, joyful'
            },
            'happy_calm': {
                'valence_min': 0.6, 'valence_max': 1.0,
                'energy_min': 0.0, 'energy_max': 0.4,
                'description': 'Peaceful, content, serene'
            },
            'sad_calm': {
                'valence_min': 0.0, 'valence_max': 0.4,
                'energy_min': 0.0, 'energy_max': 0.4,
                'description': 'Melancholic, gentle, reflective'
            },
            'sad_energetic': {
                'valence_min': 0.0, 'valence_max': 0.4,
                'energy_min': 0.6, 'energy_max': 1.0,
                'description': 'Intense, angry, aggressive'
            },
            'neutral': {
                'valence_min': 0.4, 'valence_max': 0.6,
                'energy_min': 0.4, 'energy_max': 0.6,
                'description': 'Balanced, moderate'
            }
        }
    
    def classify(self, valence: float, energy: float) -> str:
        """
        Classify a song into a mood category.
        
        Args:
            valence: Valence value (0-1, happiness)
            energy: Energy value (0-1, intensity)
            
        Returns:
            Mood category string
        """
        if valence >= 0.6 and energy >= 0.6:
            return 'happy_energetic'
        elif valence >= 0.6 and energy < 0.4:
            return 'happy_calm'
        elif valence < 0.4 and energy < 0.4:
            return 'sad_calm'
        elif valence < 0.4 and energy >= 0.6:
            return 'sad_energetic'
        else:
            return 'neutral'
    
    def classify_track(self, track_features: Dict) -> str:
        """
        Classify a track given its features dictionary.
        
        Args:
            track_features: Dictionary with 'valence' and 'energy' keys
            
        Returns:
            Mood category string
        """
        valence = track_features.get('valence', 0.5)
        energy = track_features.get('energy', 0.5)
        return self.classify(valence, energy)
    
    def classify_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Classify all tracks in a dataset.
        
        Args:
            df: DataFrame with 'valence' and 'energy' columns
            
        Returns:
            DataFrame with added 'mood' column
        """
        df = df.copy()
        df['mood'] = df.apply(
            lambda row: self.classify(row['valence'], row['energy']),
            axis=1
        )
        return df
    
    def get_mood_center(self, mood: str) -> Tuple[float, float]:
        """
        Get the center point (valence, energy) of a mood category.
        
        Args:
            mood: Mood category name
            
        Returns:
            Tuple of (valence, energy) at the center of the mood
        """
        if mood not in self.mood_definitions:
            return (0.5, 0.5)  # Neutral
        
        mood_def = self.mood_definitions[mood]
        valence_center = (mood_def['valence_min'] + mood_def['valence_max']) / 2
        energy_center = (mood_def['energy_min'] + mood_def['energy_max']) / 2
        
        return (valence_center, energy_center)
    
    def get_mood_distance(self, valence1: float, energy1: float, 
                         valence2: float, energy2: float) -> float:
        """
        Calculate Euclidean distance between two points in mood space.
        
        Args:
            valence1, energy1: First point
            valence2, energy2: Second point
            
        Returns:
            Distance between the two points
        """
        return np.sqrt((valence1 - valence2)**2 + (energy1 - energy2)**2)
    
    def get_mood_distance_to_category(self, valence: float, energy: float, 
                                      target_mood: str) -> float:
        """
        Calculate distance from a point to the center of a mood category.
        
        Args:
            valence: Valence value
            energy: Energy value
            target_mood: Target mood category
            
        Returns:
            Distance to mood category center
        """
        target_valence, target_energy = self.get_mood_center(target_mood)
        return self.get_mood_distance(valence, energy, target_valence, target_energy)
    
    def find_closest_tracks(self, df: pd.DataFrame, target_valence: float, 
                           target_energy: float, n: int = 10) -> pd.DataFrame:
        """
        Find tracks closest to a target mood point.
        
        Args:
            df: DataFrame with tracks
            target_valence: Target valence
            target_energy: Target energy
            n: Number of tracks to return
            
        Returns:
            DataFrame with n closest tracks
        """
        df = df.copy()
        df['distance'] = df.apply(
            lambda row: self.get_mood_distance(
                row['valence'], row['energy'],
                target_valence, target_energy
            ),
            axis=1
        )
        return df.nsmallest(n, 'distance')
    
    def get_mood_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get statistics about mood distribution in dataset.
        
        Args:
            df: DataFrame with 'mood' column
            
        Returns:
            DataFrame with mood statistics
        """
        if 'mood' not in df.columns:
            df = self.classify_dataset(df)
        
        stats = df.groupby('mood').agg({
            'valence': ['mean', 'std', 'min', 'max'],
            'energy': ['mean', 'std', 'min', 'max'],
            'track_id': 'count'
        }).round(3)
        
        stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
        stats = stats.rename(columns={'track_id_count': 'count'})
        
        return stats


def main():
    """Example usage of MoodClassifier"""
    import os
    
    # Load dataset
    data_path = '../data/processed/spotify_mood_dataset.csv'
    
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        print(f"Expected: {data_path}")
        print("\nPlease run the data collector first to create the dataset.")
        return
    
    print("=" * 70)
    print("MOOD CLASSIFIER - Example Usage")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} tracks")
    
    # Initialize classifier
    classifier = MoodClassifier()
    
    # Classify dataset
    print("\n🎭 Classifying tracks...")
    df = classifier.classify_dataset(df)
    
    # Show mood distribution
    print("\n📊 Mood Distribution:")
    print(df['mood'].value_counts().to_string())
    
    # Show mood statistics
    print("\n📈 Mood Statistics:")
    stats = classifier.get_mood_statistics(df)
    print(stats.to_string())
    
    # Example: Find tracks for a specific mood
    print("\n🎵 Finding tracks for 'happy_energetic' mood...")
    happy_tracks = df[df['mood'] == 'happy_energetic'].head(5)
    for idx, track in happy_tracks.iterrows():
        print(f"  • {track['name']} by {track['artist']}")
        print(f"    Valence: {track['valence']:.2f}, Energy: {track['energy']:.2f}")
    
    # Example: Find tracks closest to a specific mood point
    print("\n🎯 Finding tracks closest to (valence=0.8, energy=0.7)...")
    target_valence, target_energy = 0.8, 0.7
    closest = classifier.find_closest_tracks(df, target_valence, target_energy, n=5)
    for idx, track in closest.iterrows():
        print(f"  • {track['name']} by {track['artist']}")
        print(f"    Valence: {track['valence']:.2f}, Energy: {track['energy']:.2f}")
        print(f"    Distance: {track['distance']:.3f}")
    
    print("\n" + "=" * 70)
    print("✅ Mood classification complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
