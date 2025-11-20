"""
Collaborative Filtering for MoodShift
Provides personalized recommendations based on track similarity
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from scipy.sparse import csr_matrix


class CollaborativeFilter:
    """
    Item-based collaborative filtering using track audio features.
    Recommends similar tracks based on audio feature similarity.
    """
    
    def __init__(self, dataset: pd.DataFrame):
        """
        Initialize collaborative filter.
        
        Args:
            dataset: DataFrame with tracks and audio features
        """
        self.dataset = dataset.copy()
        self.feature_columns = [
            'valence', 'energy', 'danceability', 'acousticness',
            'instrumentalness', 'speechiness', 'tempo', 'loudness'
        ]
        
        # Keep only available features
        self.feature_columns = [col for col in self.feature_columns 
                               if col in self.dataset.columns]
        
        self.scaler = StandardScaler()
        self.similarity_matrix = None
        self.track_id_to_idx = {}
        self.idx_to_track_id = {}
        
        self._build_similarity_matrix()
    
    def _build_similarity_matrix(self):
        """Build item-item similarity matrix based on audio features."""
        print("🔨 Building similarity matrix...")
        
        # Create track ID mappings
        self.track_id_to_idx = {
            track_id: idx for idx, track_id 
            in enumerate(self.dataset['track_id'])
        }
        self.idx_to_track_id = {
            idx: track_id for track_id, idx 
            in self.track_id_to_idx.items()
        }
        
        # Extract and normalize features
        features = self.dataset[self.feature_columns].fillna(0).values
        features_normalized = self.scaler.fit_transform(features)
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(features_normalized)
        
        print(f"✓ Similarity matrix built: {self.similarity_matrix.shape}")
    
    def get_similar_tracks(self, track_id: str, n: int = 10, 
                          exclude_ids: set = None) -> List[Dict]:
        """
        Find tracks similar to a given track.
        
        Args:
            track_id: ID of the reference track
            n: Number of similar tracks to return
            exclude_ids: Set of track IDs to exclude
            
        Returns:
            List of similar tracks with similarity scores
        """
        if track_id not in self.track_id_to_idx:
            return []
        
        # Get track index
        track_idx = self.track_id_to_idx[track_id]
        
        # Get similarity scores
        similarities = self.similarity_matrix[track_idx]
        
        # Get top similar tracks
        similar_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in similar_indices:
            similar_track_id = self.idx_to_track_id[idx]
            
            # Skip the track itself
            if similar_track_id == track_id:
                continue
            
            # Skip excluded tracks
            if exclude_ids and similar_track_id in exclude_ids:
                continue
            
            # Get track info
            track_info = self.dataset[
                self.dataset['track_id'] == similar_track_id
            ].iloc[0]
            
            results.append({
                'track_id': similar_track_id,
                'name': track_info['name'],
                'artist': track_info['artist'],
                'similarity': similarities[idx],
                'valence': track_info.get('valence', 0),
                'energy': track_info.get('energy', 0)
            })
            
            if len(results) >= n:
                break
        
        return results
    
    def recommend_by_features(self, target_features: Dict, n: int = 10,
                             exclude_ids: set = None) -> List[Dict]:
        """
        Recommend tracks based on target audio features.
        
        Args:
            target_features: Dict with audio feature values
            n: Number of recommendations
            exclude_ids: Set of track IDs to exclude
            
        Returns:
            List of recommended tracks
        """
        # Create feature vector
        feature_vector = np.array([
            target_features.get(col, 0) 
            for col in self.feature_columns
        ]).reshape(1, -1)
        
        # Normalize
        feature_vector_normalized = self.scaler.transform(feature_vector)
        
        # Calculate similarities
        dataset_features = self.dataset[self.feature_columns].fillna(0).values
        dataset_features_normalized = self.scaler.transform(dataset_features)
        
        similarities = cosine_similarity(
            feature_vector_normalized,
            dataset_features_normalized
        )[0]
        
        # Get top tracks
        top_indices = np.argsort(similarities)[::-1]
        
        results = []
        for idx in top_indices:
            track = self.dataset.iloc[idx]
            track_id = track['track_id']
            
            # Skip excluded tracks
            if exclude_ids and track_id in exclude_ids:
                continue
            
            results.append({
                'track_id': track_id,
                'name': track['name'],
                'artist': track['artist'],
                'similarity': similarities[idx],
                'valence': track.get('valence', 0),
                'energy': track.get('energy', 0)
            })
            
            if len(results) >= n:
                break
        
        return results
    
    def diversify_recommendations(self, recommendations: List[Dict],
                                 diversity_weight: float = 0.3) -> List[Dict]:
        """
        Diversify recommendations to avoid too similar tracks.
        
        Args:
            recommendations: List of recommended tracks
            diversity_weight: Weight for diversity (0-1)
            
        Returns:
            Diversified list of recommendations
        """
        if len(recommendations) <= 1:
            return recommendations
        
        # Start with the top recommendation
        diversified = [recommendations[0]]
        remaining = recommendations[1:]
        
        while remaining and len(diversified) < len(recommendations):
            best_score = -1
            best_track = None
            best_idx = -1
            
            for idx, track in enumerate(remaining):
                # Original similarity score
                sim_score = track['similarity']
                
                # Calculate diversity penalty (how similar to already selected)
                min_distance = float('inf')
                for selected in diversified:
                    if selected['track_id'] in self.track_id_to_idx and \
                       track['track_id'] in self.track_id_to_idx:
                        sel_idx = self.track_id_to_idx[selected['track_id']]
                        track_idx = self.track_id_to_idx[track['track_id']]
                        distance = 1 - self.similarity_matrix[sel_idx][track_idx]
                        min_distance = min(min_distance, distance)
                
                # Combined score
                score = (1 - diversity_weight) * sim_score + \
                       diversity_weight * min_distance
                
                if score > best_score:
                    best_score = score
                    best_track = track
                    best_idx = idx
            
            if best_track:
                diversified.append(best_track)
                remaining.pop(best_idx)
        
        return diversified


def main():
    """Example usage of CollaborativeFilter"""
    import os
    
    # Load dataset
    data_path = '../data/processed/spotify_mood_dataset.csv'
    
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        return
    
    print("=" * 70)
    print("COLLABORATIVE FILTERING - Example Usage")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} tracks")
    
    # Initialize collaborative filter
    cf = CollaborativeFilter(df)
    
    # Example 1: Find similar tracks
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Find Similar Tracks")
    print("=" * 70)
    
    # Get a random track
    sample_track = df.sample(1).iloc[0]
    print(f"\nReference track: {sample_track['name']} by {sample_track['artist']}")
    print(f"Valence: {sample_track.get('valence', 0):.2f}, "
          f"Energy: {sample_track.get('energy', 0):.2f}")
    
    # Find similar
    similar = cf.get_similar_tracks(sample_track['track_id'], n=5)
    print("\nSimilar tracks:")
    for i, track in enumerate(similar, 1):
        print(f"  {i}. {track['name']} by {track['artist']}")
        print(f"     Similarity: {track['similarity']:.3f}, "
              f"V={track['valence']:.2f}, E={track['energy']:.2f}")
    
    # Example 2: Recommend by features
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Recommend by Target Features")
    print("=" * 70)
    
    target = {
        'valence': 0.8,
        'energy': 0.7,
        'danceability': 0.8
    }
    print(f"\nTarget features: {target}")
    
    recommendations = cf.recommend_by_features(target, n=5)
    print("\nRecommendations:")
    for i, track in enumerate(recommendations, 1):
        print(f"  {i}. {track['name']} by {track['artist']}")
        print(f"     Match: {track['similarity']:.3f}, "
              f"V={track['valence']:.2f}, E={track['energy']:.2f}")
    
    # Example 3: Diversified recommendations
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Diversified Recommendations")
    print("=" * 70)
    
    recommendations = cf.recommend_by_features(target, n=10)
    diversified = cf.diversify_recommendations(recommendations, diversity_weight=0.5)
    
    print("\nDiversified top 5:")
    for i, track in enumerate(diversified[:5], 1):
        print(f"  {i}. {track['name']} by {track['artist']}")
    
    print("\n" + "=" * 70)
    print("✅ Collaborative filtering complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
