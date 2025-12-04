"""
Collaborative Filtering for MoodShift
Provides track similarity and recommendations based on audio features
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Set, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler


class CollaborativeFilter:
    """
    Item-based collaborative filtering using audio features.
    Finds musically similar tracks to improve playlist cohesion.
    """
    
    def __init__(self, dataset: pd.DataFrame, verbose: bool = True):
        """
        Initialize collaborative filter and build similarity matrix.
        
        Args:
            dataset: DataFrame with tracks and audio features
            verbose: Print progress messages
        """
        self.dataset = dataset.copy()
        self.verbose = verbose
        
        # Audio features to use for similarity
        self.feature_columns = [
            'valence', 'energy', 'danceability', 'acousticness',
            'instrumentalness', 'speechiness', 'tempo', 'loudness'
        ]
        
        # Keep only features that exist in dataset
        self.feature_columns = [
            col for col in self.feature_columns 
            if col in self.dataset.columns
        ]
        
        if len(self.feature_columns) < 2:
            raise ValueError(
                f"Dataset must have at least 2 audio features. "
                f"Found: {self.feature_columns}"
            )
        
        self.scaler = StandardScaler()
        self.similarity_matrix = None
        self.track_id_to_idx = {}
        self.idx_to_track_id = {}
        
        # Build the similarity matrix
        self._build_similarity_matrix()
    
    def _build_similarity_matrix(self):
        """Build item-item similarity matrix using audio features."""
        if self.verbose:
            print(f"🔨 Building CF similarity matrix...")
            print(f"   Using features: {', '.join(self.feature_columns)}")
        
        # Create track ID mappings
        self.track_id_to_idx = {
            track_id: idx 
            for idx, track_id in enumerate(self.dataset['track_id'])
        }
        self.idx_to_track_id = {
            idx: track_id 
            for track_id, idx in self.track_id_to_idx.items()
        }
        
        # Extract and normalize features
        features = self.dataset[self.feature_columns].fillna(0).values
        features_normalized = self.scaler.fit_transform(features)
        
        # Calculate cosine similarity
        self.similarity_matrix = cosine_similarity(features_normalized)
        
        if self.verbose:
            print(f"✓ Similarity matrix built: {self.similarity_matrix.shape}")
            print(f"   {len(self.dataset)} tracks indexed")
    
    def get_similar_tracks(self, track_id: str, n: int = 10, 
                          exclude_ids: Optional[Set[str]] = None) -> List[Dict]:
        """
        Find tracks most similar to a given track.
        
        Args:
            track_id: ID of the reference track
            n: Number of similar tracks to return
            exclude_ids: Set of track IDs to exclude from results
            
        Returns:
            List of similar tracks with similarity scores
            Each dict contains: track_id, name, artist, similarity, valence, energy
        """
        # Check if track exists
        if track_id not in self.track_id_to_idx:
            if self.verbose:
                print(f"⚠️  Track {track_id} not found in dataset")
            return []
        
        # Get track index
        track_idx = self.track_id_to_idx[track_id]
        
        # Get similarity scores for this track
        similarities = self.similarity_matrix[track_idx]
        
        # Get indices sorted by similarity (descending)
        similar_indices = np.argsort(similarities)[::-1]
        
        # Build results
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
                'similarity': float(similarities[idx]),
                'valence': float(track_info.get('valence', 0)),
                'energy': float(track_info.get('energy', 0))
            })
            
            if len(results) >= n:
                break
        
        return results
    
    def get_similarity_score(self, track_id1: str, track_id2: str) -> float:
        """
        Get similarity score between two specific tracks.
        
        Args:
            track_id1: First track ID
            track_id2: Second track ID
            
        Returns:
            Similarity score (0-1, where 1 is most similar)
        """
        if track_id1 not in self.track_id_to_idx:
            return 0.0
        if track_id2 not in self.track_id_to_idx:
            return 0.0
        
        idx1 = self.track_id_to_idx[track_id1]
        idx2 = self.track_id_to_idx[track_id2]
        
        return float(self.similarity_matrix[idx1][idx2])
    
    def recommend_by_features(self, target_features: Dict, n: int = 10,
                             exclude_ids: Optional[Set[str]] = None) -> List[Dict]:
        """
        Recommend tracks based on target audio features.
        
        Args:
            target_features: Dict with audio feature values
                           e.g., {'valence': 0.8, 'energy': 0.7}
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
        
        # Normalize using same scaler
        feature_vector_normalized = self.scaler.transform(feature_vector)
        
        # Get normalized dataset features
        dataset_features = self.dataset[self.feature_columns].fillna(0).values
        dataset_features_normalized = self.scaler.transform(dataset_features)
        
        # Calculate similarities
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
                'similarity': float(similarities[idx]),
                'valence': float(track.get('valence', 0)),
                'energy': float(track.get('energy', 0))
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
            diversity_weight: Weight for diversity vs similarity (0-1)
                            Higher = more diverse
            
        Returns:
            Diversified list of recommendations
        """
        if len(recommendations) <= 1:
            return recommendations
        
        # Start with top recommendation
        diversified = [recommendations[0]]
        remaining = recommendations[1:]
        
        while remaining and len(diversified) < len(recommendations):
            best_score = -1
            best_track = None
            best_idx = -1
            
            for idx, track in enumerate(remaining):
                # Original similarity score (to seed/features)
                sim_score = track['similarity']
                
                # Calculate diversity penalty
                # How different is this from already selected tracks?
                min_distance = float('inf')
                for selected in diversified:
                    if (selected['track_id'] in self.track_id_to_idx and 
                        track['track_id'] in self.track_id_to_idx):
                        
                        # Get similarity between this track and selected
                        sel_idx = self.track_id_to_idx[selected['track_id']]
                        track_idx = self.track_id_to_idx[track['track_id']]
                        similarity = self.similarity_matrix[sel_idx][track_idx]
                        distance = 1 - similarity
                        min_distance = min(min_distance, distance)
                
                # Combined score (higher is better)
                score = (
                    (1 - diversity_weight) * sim_score + 
                    diversity_weight * min_distance
                )
                
                if score > best_score:
                    best_score = score
                    best_track = track
                    best_idx = idx
            
            if best_track:
                diversified.append(best_track)
                remaining.pop(best_idx)
        
        return diversified
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the similarity matrix.
        
        Returns:
            Dict with statistics
        """
        # Calculate average similarities
        # Exclude diagonal (self-similarity)
        np.fill_diagonal(self.similarity_matrix, 0)
        
        stats = {
            'num_tracks': len(self.dataset),
            'num_features': len(self.feature_columns),
            'avg_similarity': float(np.mean(self.similarity_matrix)),
            'max_similarity': float(np.max(self.similarity_matrix)),
            'min_similarity': float(np.min(self.similarity_matrix)),
            'features_used': self.feature_columns
        }
        
        # Restore diagonal
        np.fill_diagonal(self.similarity_matrix, 1)
        
        return stats


def main():
    """Example usage and testing"""
    import os
    
    # Try to load dataset
    data_path = '../data/processed/spotify_mood_dataset.csv'
    
    if not os.path.exists(data_path):
        print("❌ Dataset not found!")
        print(f"Expected: {data_path}")
        print("\nPlease update the path or create a test dataset.")
        return
    
    print("=" * 70)
    print("COLLABORATIVE FILTERING - Testing")
    print("=" * 70)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} tracks")
    
    # Initialize CF
    print("\n🔧 Initializing Collaborative Filter...")
    cf = CollaborativeFilter(df)
    
    # Get statistics
    print("\n📊 CF Statistics:")
    stats = cf.get_statistics()
    for key, value in stats.items():
        if key == 'features_used':
            print(f"  {key}: {', '.join(value)}")
        else:
            print(f"  {key}: {value}")
    
    # Test 1: Find similar tracks
    print("\n" + "=" * 70)
    print("TEST 1: Find Similar Tracks")
    print("=" * 70)
    
    sample_track = df.sample(1).iloc[0]
    print(f"\nReference track:")
    print(f"  {sample_track['name']} by {sample_track['artist']}")
    print(f"  Valence: {sample_track.get('valence', 0):.2f}, "
          f"Energy: {sample_track.get('energy', 0):.2f}")
    
    similar = cf.get_similar_tracks(sample_track['track_id'], n=5)
    print(f"\nTop 5 similar tracks:")
    for i, track in enumerate(similar, 1):
        print(f"  {i}. {track['name']} by {track['artist']}")
        print(f"     Similarity: {track['similarity']:.3f}, "
              f"V={track['valence']:.2f}, E={track['energy']:.2f}")
    
    # Test 2: Recommend by features
    print("\n" + "=" * 70)
    print("TEST 2: Recommend by Features")
    print("=" * 70)
    
    target = {'valence': 0.8, 'energy': 0.7, 'danceability': 0.8}
    print(f"\nTarget features: {target}")
    
    recommendations = cf.recommend_by_features(target, n=5)
    print(f"\nTop 5 recommendations:")
    for i, track in enumerate(recommendations, 1):
        print(f"  {i}. {track['name']} by {track['artist']}")
        print(f"     Match: {track['similarity']:.3f}")
    
    # Test 3: Diversification
    print("\n" + "=" * 70)
    print("TEST 3: Diversify Recommendations")
    print("=" * 70)
    
    recommendations = cf.recommend_by_features(target, n=10)
    diversified = cf.diversify_recommendations(
        recommendations, 
        diversity_weight=0.5
    )
    
    print(f"\nOriginal top 5:")
    for i, track in enumerate(recommendations[:5], 1):
        print(f"  {i}. {track['name']}")
    
    print(f"\nDiversified top 5:")
    for i, track in enumerate(diversified[:5], 1):
        print(f"  {i}. {track['name']}")
    
    print("\n" + "=" * 70)
    print("✅ Collaborative Filtering tests complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
