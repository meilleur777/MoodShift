"""
Data Analysis Utilities for MoodShift Dataset
Analyze and visualize the collected music data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple


class DatasetAnalyzer:
    def __init__(self, csv_path: str):
        """
        Initialize with a dataset CSV file
        
        Args:
            csv_path: Path to the CSV file
        """
        self.df = pd.read_csv(csv_path)
        print(f"Loaded dataset with {len(self.df)} tracks")
    
    def basic_statistics(self):
        """Display basic statistics about the dataset"""
        print("\n" + "=" * 60)
        print("BASIC STATISTICS")
        print("=" * 60)
        
        print(f"\nTotal tracks: {len(self.df)}")
        print(f"Unique artists: {self.df['artist'].nunique()}")
        
        if 'mood_category' in self.df.columns:
            print("\nTracks per mood category:")
            print(self.df['mood_category'].value_counts())
        
        print("\nAudio Features Summary:")
        feature_cols = ['valence', 'energy', 'danceability', 'acousticness', 
                       'instrumentalness', 'speechiness', 'tempo']
        print(self.df[feature_cols].describe())
        
        print("\nMissing values:")
        print(self.df.isnull().sum())
    
    def mood_distribution(self):
        """Analyze mood distribution based on valence and energy"""
        print("\n" + "=" * 60)
        print("MOOD DISTRIBUTION ANALYSIS")
        print("=" * 60)
        
        # Create mood quadrants based on valence and energy
        self.df['mood_quadrant'] = 'neutral'
        
        self.df.loc[(self.df['valence'] >= 0.5) & (self.df['energy'] >= 0.5), 'mood_quadrant'] = 'happy_energetic'
        self.df.loc[(self.df['valence'] >= 0.5) & (self.df['energy'] < 0.5), 'mood_quadrant'] = 'happy_calm'
        self.df.loc[(self.df['valence'] < 0.5) & (self.df['energy'] >= 0.5), 'mood_quadrant'] = 'tense_energetic'
        self.df.loc[(self.df['valence'] < 0.5) & (self.df['energy'] < 0.5), 'mood_quadrant'] = 'sad_calm'
        
        print("\nMood quadrant distribution:")
        print(self.df['mood_quadrant'].value_counts())
        
        print("\nAverage features per mood quadrant:")
        mood_features = self.df.groupby('mood_quadrant')[['valence', 'energy', 'danceability', 'tempo']].mean()
        print(mood_features)
    
    def visualize_mood_space(self, save_path: str = 'mood_space.png'):
        """
        Visualize the mood space (valence vs energy)
        
        Args:
            save_path: Path to save the visualization
        """
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot
        if 'mood_category' in self.df.columns:
            scatter = plt.scatter(self.df['valence'], self.df['energy'], 
                                c=pd.Categorical(self.df['mood_category']).codes,
                                cmap='viridis', alpha=0.6, s=50)
            plt.colorbar(scatter, label='Mood Category')
        else:
            plt.scatter(self.df['valence'], self.df['energy'], alpha=0.6, s=50)
        
        plt.xlabel('Valence (Happiness)', fontsize=12)
        plt.ylabel('Energy', fontsize=12)
        plt.title('Mood Space Distribution (Valence vs Energy)', fontsize=14, fontweight='bold')
        
        # Add quadrant lines
        plt.axhline(y=0.5, color='r', linestyle='--', alpha=0.3)
        plt.axvline(x=0.5, color='r', linestyle='--', alpha=0.3)
        
        # Add quadrant labels
        plt.text(0.75, 0.75, 'Happy\nEnergetic', ha='center', va='center', 
                fontsize=10, alpha=0.5, fontweight='bold')
        plt.text(0.75, 0.25, 'Happy\nCalm', ha='center', va='center', 
                fontsize=10, alpha=0.5, fontweight='bold')
        plt.text(0.25, 0.75, 'Tense\nEnergetic', ha='center', va='center', 
                fontsize=10, alpha=0.5, fontweight='bold')
        plt.text(0.25, 0.25, 'Sad\nCalm', ha='center', va='center', 
                fontsize=10, alpha=0.5, fontweight='bold')
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nMood space visualization saved to '{save_path}'")
        plt.close()
    
    def feature_correlations(self, save_path: str = 'feature_correlations.png'):
        """
        Analyze and visualize feature correlations
        
        Args:
            save_path: Path to save the correlation heatmap
        """
        print("\n" + "=" * 60)
        print("FEATURE CORRELATIONS")
        print("=" * 60)
        
        feature_cols = ['valence', 'energy', 'danceability', 'acousticness', 
                       'instrumentalness', 'speechiness', 'loudness', 'tempo']
        
        correlation_matrix = self.df[feature_cols].corr()
        
        print("\nCorrelation Matrix:")
        print(correlation_matrix)
        
        # Create heatmap
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                   fmt='.2f', square=True, linewidths=1)
        plt.title('Audio Feature Correlations', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nCorrelation heatmap saved to '{save_path}'")
        plt.close()
    
    def tempo_distribution(self, save_path: str = 'tempo_distribution.png'):
        """
        Analyze tempo distribution across moods
        
        Args:
            save_path: Path to save the visualization
        """
        plt.figure(figsize=(12, 6))
        
        if 'mood_category' in self.df.columns:
            self.df.boxplot(column='tempo', by='mood_category', figsize=(12, 6))
            plt.title('Tempo Distribution by Mood Category')
            plt.suptitle('')  # Remove default title
            plt.xlabel('Mood Category')
        else:
            plt.hist(self.df['tempo'], bins=50, edgecolor='black', alpha=0.7)
            plt.xlabel('Tempo (BPM)')
            plt.title('Tempo Distribution')
        
        plt.ylabel('Tempo (BPM)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\nTempo distribution saved to '{save_path}'")
        plt.close()
    
    def find_mood_extremes(self):
        """Find tracks at mood extremes"""
        print("\n" + "=" * 60)
        print("MOOD EXTREMES")
        print("=" * 60)
        
        print("\nHappiest tracks (highest valence):")
        happiest = self.df.nlargest(5, 'valence')[['name', 'artist', 'valence', 'energy']]
        print(happiest.to_string(index=False))
        
        print("\nSaddest tracks (lowest valence):")
        saddest = self.df.nsmallest(5, 'valence')[['name', 'artist', 'valence', 'energy']]
        print(saddest.to_string(index=False))
        
        print("\nMost energetic tracks:")
        energetic = self.df.nlargest(5, 'energy')[['name', 'artist', 'valence', 'energy']]
        print(energetic.to_string(index=False))
        
        print("\nMost calm tracks:")
        calm = self.df.nsmallest(5, 'energy')[['name', 'artist', 'valence', 'energy']]
        print(calm.to_string(index=False))
    
    def export_mood_categories(self, output_path: str = 'mood_categories.csv'):
        """
        Export dataset with computed mood quadrants
        
        Args:
            output_path: Path to save the updated dataset
        """
        # Ensure mood_quadrant column exists
        if 'mood_quadrant' not in self.df.columns:
            self.mood_distribution()
        
        self.df.to_csv(output_path, index=False)
        print(f"\nDataset with mood categories saved to '{output_path}'")
    
    def data_quality_check(self):
        """Check data quality and identify potential issues"""
        print("\n" + "=" * 60)
        print("DATA QUALITY CHECK")
        print("=" * 60)
        
        # Check for duplicates
        duplicates = self.df.duplicated(subset=['track_id']).sum()
        print(f"\nDuplicate tracks: {duplicates}")
        
        # Check for missing values
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print("\nMissing values:")
            print(missing[missing > 0])
        else:
            print("\nNo missing values found!")
        
        # Check for outliers in audio features
        print("\nPotential outliers (values outside expected ranges):")
        
        # Features that should be between 0 and 1
        normalized_features = ['valence', 'energy', 'danceability', 'acousticness', 
                              'instrumentalness', 'speechiness', 'liveness']
        
        for feature in normalized_features:
            outliers = ((self.df[feature] < 0) | (self.df[feature] > 1)).sum()
            if outliers > 0:
                print(f"  {feature}: {outliers} outliers")
        
        # Check tempo range
        tempo_low = (self.df['tempo'] < 40).sum()
        tempo_high = (self.df['tempo'] > 200).sum()
        if tempo_low > 0 or tempo_high > 0:
            print(f"  tempo: {tempo_low} below 40 BPM, {tempo_high} above 200 BPM")


def main():
    """Example usage of DatasetAnalyzer"""
    
    # Load the dataset
    analyzer = DatasetAnalyzer('spotify_mood_dataset.csv')
    
    # Run all analyses
    analyzer.basic_statistics()
    analyzer.mood_distribution()
    analyzer.data_quality_check()
    analyzer.find_mood_extremes()
    analyzer.feature_correlations()
    
    # Create visualizations
    analyzer.visualize_mood_space()
    analyzer.tempo_distribution()
    
    # Export enhanced dataset
    analyzer.export_mood_categories('spotify_mood_dataset_enhanced.csv')
    
    print("\n" + "=" * 60)
    print("Analysis complete! Check the generated PNG files for visualizations.")
    print("=" * 60)


if __name__ == "__main__":
    main()
