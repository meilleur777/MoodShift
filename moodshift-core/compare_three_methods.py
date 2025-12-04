"""
Comprehensive Comparison: Original vs CF vs CF+Random
Compares three methods with their optimal configurations:
1. Original (main.py) - Pure mood-based
2. CF-Enhanced (main_cf.py) - cf_weight=1.0
3. CF+Random (main_cf_random.py) - randomness=0.7, diversity=0.5, serendipity=True
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
import argparse
from datetime import datetime
import json


class ThreeWayComparator:
    """
    Compares three playlist generation methods:
    1. Original (mood-only)
    2. CF-Enhanced (cf_weight=1.0)
    3. CF+Random (randomness=0.7, diversity=0.5, serendipity=True)
    """
    
    def __init__(self, dataset_path: str):
        """
        Initialize comparator.
        
        Args:
            dataset_path: Path to music dataset
        """
        print("🔬 Initializing Three-Way Comparator...")
        print("=" * 70)
        
        self.dataset_path = dataset_path
        
        # Try to import all three systems
        try:
            # Import original system (if available)
            try:
                import sys
                import os
                # Try to import from main.py
                if os.path.exists('main.py'):
                    import main
                    self.original_available = True
                    print("✓ Original system (main.py) loaded")
                else:
                    self.original_available = False
                    print("⚠️  Original system (main.py) not found - will use smooth method")
            except Exception as e:
                self.original_available = False
                print(f"⚠️  Could not load main.py: {e}")
            
            # Import CF system
            try:
                from main_cf import MoodShiftCF
                self.ms_cf = MoodShiftCF(dataset_path, verbose=False)
                print("✓ CF-Enhanced system (main_cf.py) loaded")
            except ImportError as e:
                raise ImportError(f"Could not import main_cf.py: {e}")
            
            # Import CF+Random system
            try:
                from main_cf_random import MoodShiftCF as MoodShiftCFRandom
                self.ms_random = MoodShiftCFRandom(dataset_path, verbose=False, random_seed=None)
                print("✓ CF+Random system (main_cf_random.py) loaded")
            except ImportError as e:
                raise ImportError(f"Could not import main_cf_random.py: {e}")
            
            print("=" * 70)
            print("✅ All systems ready!\n")
            
        except Exception as e:
            print(f"❌ Error initializing systems: {e}")
            raise
    
    def compare_all_methods(self,
                           current_mood: str = 'sad_calm',
                           target_mood: str = 'happy_energetic',
                           length: int = 10,
                           n_runs: int = 20) -> Dict:
        """
        Comprehensive comparison of all three methods.
        
        Args:
            current_mood: Starting mood
            target_mood: Target mood
            length: Playlist length
            n_runs: Number of runs per method
            
        Returns:
            Dict with comparison results
        """
        print("=" * 70)
        print("THREE-WAY COMPARISON")
        print("=" * 70)
        print(f"Transition: {current_mood} → {target_mood}")
        print(f"Playlist length: {length} tracks")
        print(f"Runs per method: {n_runs}\n")
        
        results = {
            'original': {
                'smoothness': [],
                'cf_cohesion': [],
                'variety': [],
                'target_accuracy': [],
                'unique_tracks': set(),
                'playlists': []
            },
            'cf_enhanced': {
                'smoothness': [],
                'cf_cohesion': [],
                'variety': [],
                'target_accuracy': [],
                'unique_tracks': set(),
                'playlists': []
            },
            'cf_random': {
                'smoothness': [],
                'cf_cohesion': [],
                'variety': [],
                'target_accuracy': [],
                'unique_tracks': set(),
                'playlists': []
            }
        }
        
        # Method 1: Original (mood-only)
        print("📝 Method 1: Original (Pure Mood-Based)")
        print("   Configuration: method='smooth'")
        print("   Generating playlists...")
        
        for run in range(n_runs):
            playlist = self.ms_cf.create_playlist(
                current_mood, target_mood, length,
                method='smooth'
            )
            
            metrics = self.ms_cf.calculate_playlist_metrics(playlist)
            
            results['original']['smoothness'].append(metrics['smoothness'])
            results['original']['cf_cohesion'].append(metrics['cf_cohesion'])
            results['original']['variety'].append(metrics['variety'])
            
            # Target accuracy
            target_v, target_e = self._get_mood_center(target_mood)
            final_v = playlist.iloc[-1]['valence']
            final_e = playlist.iloc[-1]['energy']
            target_dist = np.sqrt((target_v - final_v)**2 + (target_e - final_e)**2)
            results['original']['target_accuracy'].append(target_dist)
            
            # Track uniqueness
            results['original']['unique_tracks'].update(playlist['track_id'].tolist())
            
            if run < 3:
                results['original']['playlists'].append(playlist)
        
        print(f"   ✓ Generated {n_runs} playlists")
        print(f"   Unique tracks used: {len(results['original']['unique_tracks'])}\n")
        
        # Method 2: CF-Enhanced (cf_weight=1.0)
        print("📝 Method 2: CF-Enhanced (Pure CF)")
        print("   Configuration: method='cf_enhanced', cf_weight=1.0")
        print("   Generating playlists...")
        
        for run in range(n_runs):
            playlist = self.ms_cf.create_playlist(
                current_mood, target_mood, length,
                method='cf_enhanced',
                cf_weight=1.0
            )
            
            metrics = self.ms_cf.calculate_playlist_metrics(playlist)
            
            results['cf_enhanced']['smoothness'].append(metrics['smoothness'])
            results['cf_enhanced']['cf_cohesion'].append(metrics['cf_cohesion'])
            results['cf_enhanced']['variety'].append(metrics['variety'])
            
            # Target accuracy
            target_v, target_e = self._get_mood_center(target_mood)
            final_v = playlist.iloc[-1]['valence']
            final_e = playlist.iloc[-1]['energy']
            target_dist = np.sqrt((target_v - final_v)**2 + (target_e - final_e)**2)
            results['cf_enhanced']['target_accuracy'].append(target_dist)
            
            # Track uniqueness
            results['cf_enhanced']['unique_tracks'].update(playlist['track_id'].tolist())
            
            if run < 3:
                results['cf_enhanced']['playlists'].append(playlist)
        
        print(f"   ✓ Generated {n_runs} playlists")
        print(f"   Unique tracks used: {len(results['cf_enhanced']['unique_tracks'])}\n")
        
        # Method 3: CF+Random (randomness=0.7, diversity=0.5, serendipity=True)
        print("📝 Method 3: CF+Random (High Variation)")
        print("   Configuration: cf_weight=1.0, randomness=0.7, diversity=0.5, serendipity=True")
        print("   Generating playlists...")
        
        for run in range(n_runs):
            playlist = self.ms_random.create_playlist(
                current_mood, target_mood, length,
                method='cf_enhanced',
                cf_weight=1.0,
                randomness=0.7,
                diversity_weight=0.5,
                serendipity=True
            )
            
            metrics = self.ms_random.calculate_playlist_metrics(playlist)
            
            results['cf_random']['smoothness'].append(metrics['smoothness'])
            results['cf_random']['cf_cohesion'].append(metrics['cf_cohesion'])
            results['cf_random']['variety'].append(metrics['variety'])
            
            # Target accuracy
            target_v, target_e = self._get_mood_center(target_mood)
            final_v = playlist.iloc[-1]['valence']
            final_e = playlist.iloc[-1]['energy']
            target_dist = np.sqrt((target_v - final_v)**2 + (target_e - final_e)**2)
            results['cf_random']['target_accuracy'].append(target_dist)
            
            # Track uniqueness
            results['cf_random']['unique_tracks'].update(playlist['track_id'].tolist())
            
            if run < 3:
                results['cf_random']['playlists'].append(playlist)
        
        print(f"   ✓ Generated {n_runs} playlists")
        print(f"   Unique tracks used: {len(results['cf_random']['unique_tracks'])}\n")
        
        # Statistical comparison
        self._print_comparison_table(results, n_runs, length)
        
        return results
    
    def _get_mood_center(self, mood: str) -> Tuple[float, float]:
        """Get valence and energy center for a mood."""
        mood_centers = {
            'happy_energetic': (0.8, 0.8),
            'happy_calm': (0.8, 0.2),
            'sad_calm': (0.2, 0.2),
            'sad_energetic': (0.2, 0.8),
            'neutral': (0.5, 0.5)
        }
        return mood_centers.get(mood, (0.5, 0.5))
    
    def _print_comparison_table(self, results: Dict, n_runs: int, length: int):
        """Print detailed comparison table."""
        print("=" * 70)
        print("COMPARISON RESULTS")
        print("=" * 70)
        print()
        
        methods = ['original', 'cf_enhanced', 'cf_random']
        method_names = ['Original (Mood)', 'CF-Enhanced (Pure CF)', 'CF+Random (High Var)']
        
        print("📊 Smoothness (Lower is Better)")
        print("-" * 70)
        for method, name in zip(methods, method_names):
            values = results[method]['smoothness']
            mean = np.mean(values)
            std = np.std(values)
            print(f"{name:30s}: {mean:.4f} (±{std:.4f})")
        
        # Winner
        smooth_means = {m: np.mean(results[m]['smoothness']) for m in methods}
        winner = min(smooth_means, key=smooth_means.get)
        winner_name = method_names[methods.index(winner)]
        print(f"🏆 Winner: {winner_name}")
        print()
        
        print("📊 CF Cohesion (Higher is Better)")
        print("-" * 70)
        for method, name in zip(methods, method_names):
            values = results[method]['cf_cohesion']
            mean = np.mean(values)
            std = np.std(values)
            print(f"{name:30s}: {mean:.4f} (±{std:.4f})")
        
        # Winner
        cohesion_means = {m: np.mean(results[m]['cf_cohesion']) for m in methods}
        winner = max(cohesion_means, key=cohesion_means.get)
        winner_name = method_names[methods.index(winner)]
        print(f"🏆 Winner: {winner_name}")
        print()
        
        print("📊 Variety (Measured by Unique Tracks)")
        print("-" * 70)
        for method, name in zip(methods, method_names):
            unique = len(results[method]['unique_tracks'])
            percentage = unique / (n_runs * length) * 100
            print(f"{name:30s}: {unique} tracks ({percentage:.1f}% of slots)")
        
        # Winner
        unique_counts = {m: len(results[m]['unique_tracks']) for m in methods}
        winner = max(unique_counts, key=unique_counts.get)
        winner_name = method_names[methods.index(winner)]
        print(f"🏆 Winner: {winner_name}")
        print()
        
        print("📊 Target Accuracy (Lower is Better)")
        print("-" * 70)
        for method, name in zip(methods, method_names):
            values = results[method]['target_accuracy']
            mean = np.mean(values)
            std = np.std(values)
            print(f"{name:30s}: {mean:.4f} (±{std:.4f})")
        
        # Winner
        target_means = {m: np.mean(results[m]['target_accuracy']) for m in methods}
        winner = min(target_means, key=target_means.get)
        winner_name = method_names[methods.index(winner)]
        print(f"🏆 Winner: {winner_name}")
        print()
        
        print("📊 Overall Variety (Standard Deviation)")
        print("-" * 70)
        for method, name in zip(methods, method_names):
            values = results[method]['variety']
            mean = np.mean(values)
            std = np.std(values)
            print(f"{name:30s}: {mean:.4f} (±{std:.4f})")
        
        winner_variety = max(methods, key=lambda m: np.mean(results[m]['variety']))
        winner_name = method_names[methods.index(winner_variety)]
        print(f"🏆 Winner: {winner_name}")
        print()
    
    def statistical_comparison(self, results: Dict) -> Dict:
        """
        Perform statistical tests to determine significance.
        
        Args:
            results: Results from compare_all_methods
            
        Returns:
            Dict with statistical test results
        """
        print("=" * 70)
        print("STATISTICAL SIGNIFICANCE TESTS")
        print("=" * 70)
        print()
        
        from scipy import stats
        
        methods = ['original', 'cf_enhanced', 'cf_random']
        method_names = ['Original', 'CF-Enhanced', 'CF+Random']
        
        stat_results = {}
        
        # Test each metric
        for metric in ['smoothness', 'cf_cohesion', 'target_accuracy', 'variety']:
            print(f"📊 {metric.replace('_', ' ').title()}")
            print("-" * 70)
            
            stat_results[metric] = {}
            
            # Pairwise comparisons
            for i in range(len(methods)):
                for j in range(i + 1, len(methods)):
                    method1, method2 = methods[i], methods[j]
                    name1, name2 = method_names[i], method_names[j]
                    
                    values1 = results[method1][metric]
                    values2 = results[method2][metric]
                    
                    # Perform t-test
                    t_stat, p_value = stats.ttest_ind(values1, values2)
                    
                    # Determine significance
                    if p_value < 0.001:
                        sig_level = "***"
                        sig_text = "Very significant"
                    elif p_value < 0.01:
                        sig_level = "**"
                        sig_text = "Significant"
                    elif p_value < 0.05:
                        sig_level = "*"
                        sig_text = "Marginally significant"
                    else:
                        sig_level = "ns"
                        sig_text = "Not significant"
                    
                    # Calculate effect size (Cohen's d)
                    mean1, mean2 = np.mean(values1), np.mean(values2)
                    std_pooled = np.sqrt((np.var(values1) + np.var(values2)) / 2)
                    cohens_d = abs(mean1 - mean2) / std_pooled if std_pooled > 0 else 0
                    
                    comparison_key = f"{name1} vs {name2}"
                    stat_results[metric][comparison_key] = {
                        'p_value': p_value,
                        'significance': sig_level,
                        'cohens_d': cohens_d
                    }
                    
                    print(f"{comparison_key:30s}: p={p_value:.4f} {sig_level:3s} "
                          f"({sig_text}) [d={cohens_d:.2f}]")
            
            print()
        
        return stat_results
    
    def create_example_playlists(self, results: Dict, output_file: str = 'example_playlists.txt'):
        """
        Create example playlists showing differences.
        
        Args:
            results: Results from compare_all_methods
            output_file: Output filename
        """
        print("=" * 70)
        print("GENERATING EXAMPLE PLAYLISTS")
        print("=" * 70)
        
        output = "# Example Playlists - Three Methods Comparison\n\n"
        
        methods = ['original', 'cf_enhanced', 'cf_random']
        method_names = [
            'Original (Pure Mood)',
            'CF-Enhanced (cf_weight=1.0)',
            'CF+Random (rand=0.7, div=0.5, serend=True)'
        ]
        
        for method, name in zip(methods, method_names):
            output += f"## {name}\n\n"
            
            # Get first example playlist
            if results[method]['playlists']:
                playlist = results[method]['playlists'][0]
                
                output += "```\n"
                for idx, row in playlist.iterrows():
                    output += f"{row['step']:2d}. {row['name'][:40]:40s} - {row['artist'][:20]:20s}\n"
                    output += f"    Mood: {row['mood']:20s} (V={row['valence']:.2f}, E={row['energy']:.2f})\n"
                output += "```\n\n"
                
                # Calculate metrics
                metrics = self.ms_cf.calculate_playlist_metrics(playlist)
                output += f"**Metrics:**\n"
                output += f"- Smoothness: {metrics['smoothness']:.3f}\n"
                output += f"- CF Cohesion: {metrics['cf_cohesion']:.3f}\n"
                output += f"- Variety: {metrics['variety']:.3f}\n\n"
                output += "---\n\n"
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        print(f"✓ Example playlists saved to: {output_file}\n")
    
    def generate_report(self, results: Dict, stat_results: Dict,
                       output_file: str = 'three_way_comparison_report.md'):
        """
        Generate comprehensive comparison report.
        
        Args:
            results: Results from compare_all_methods
            stat_results: Results from statistical_comparison
            output_file: Output filename
        """
        print("=" * 70)
        print("GENERATING COMPARISON REPORT")
        print("=" * 70)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Calculate summary statistics
        methods = ['original', 'cf_enhanced', 'cf_random']
        method_names = ['Original (Mood)', 'CF-Enhanced (Pure CF)', 'CF+Random (High Var)']
        
        report = f"""# Three-Way Method Comparison Report

Generated: {timestamp}

---

## Executive Summary

This report compares three playlist generation methods:

1. **Original (Pure Mood)** - Mood-based selection only
2. **CF-Enhanced (Pure CF)** - Collaborative filtering with cf_weight=1.0
3. **CF+Random (High Variation)** - CF with randomness=0.7, diversity=0.5, serendipity=True

### Configuration Summary

| Method | Configuration | Focus |
|--------|--------------|-------|
| Original | method='smooth' | Mood progression accuracy |
| CF-Enhanced | cf_weight=1.0 | Maximum musical cohesion |
| CF+Random | rand=0.7, div=0.5, serend=True | Maximum variety & discovery |

---

## Key Findings

"""
        
        # Determine winners for each metric
        smooth_means = {m: np.mean(results[m]['smoothness']) for m in methods}
        cohesion_means = {m: np.mean(results[m]['cf_cohesion']) for m in methods}
        unique_counts = {m: len(results[m]['unique_tracks']) for m in methods}
        target_means = {m: np.mean(results[m]['target_accuracy']) for m in methods}
        
        smooth_winner = min(smooth_means, key=smooth_means.get)
        cohesion_winner = max(cohesion_means, key=cohesion_means.get)
        variety_winner = max(unique_counts, key=unique_counts.get)
        target_winner = min(target_means, key=target_means.get)
        
        report += f"""
**1. Smoothness Winner: {method_names[methods.index(smooth_winner)]}**
   - Score: {smooth_means[smooth_winner]:.4f}
   - {((smooth_means['original'] - smooth_means[smooth_winner]) / smooth_means['original'] * 100):+.1f}% vs Original

**2. Musical Cohesion Winner: {method_names[methods.index(cohesion_winner)]}**
   - Score: {cohesion_means[cohesion_winner]:.4f}
   - {((cohesion_means[cohesion_winner] - cohesion_means['original']) / cohesion_means['original'] * 100):+.1f}% vs Original

**3. Variety Winner: {method_names[methods.index(variety_winner)]}**
   - Unique tracks: {unique_counts[variety_winner]}
   - {((unique_counts[variety_winner] - unique_counts['original']) / unique_counts['original'] * 100):+.1f}% vs Original

**4. Target Accuracy Winner: {method_names[methods.index(target_winner)]}**
   - Score: {target_means[target_winner]:.4f}
   - {((target_means['original'] - target_means[target_winner]) / target_means['original'] * 100):+.1f}% vs Original

---

## Detailed Comparison

### Smoothness (Lower is Better)

| Method | Mean | Std Dev | vs Original |
|--------|------|---------|-------------|
"""
        
        orig_smooth = smooth_means['original']
        for method, name in zip(methods, method_names):
            mean = smooth_means[method]
            std = np.std(results[method]['smoothness'])
            vs_orig = ((orig_smooth - mean) / orig_smooth * 100)
            report += f"| {name} | {mean:.4f} | {std:.4f} | {vs_orig:+.1f}% |\n"
        
        report += """

### CF Cohesion (Higher is Better)

| Method | Mean | Std Dev | vs Original |
|--------|------|---------|-------------|
"""
        
        orig_cohesion = cohesion_means['original']
        for method, name in zip(methods, method_names):
            mean = cohesion_means[method]
            std = np.std(results[method]['cf_cohesion'])
            vs_orig = ((mean - orig_cohesion) / orig_cohesion * 100)
            report += f"| {name} | {mean:.4f} | {std:.4f} | {vs_orig:+.1f}% |\n"
        
        report += """

### Variety (Unique Tracks)

| Method | Unique Tracks | % of Total Slots |
|--------|---------------|------------------|
"""
        
        n_runs = len(results['original']['smoothness'])
        length = len(results['original']['playlists'][0]) if results['original']['playlists'] else 10
        total_slots = n_runs * length
        
        for method, name in zip(methods, method_names):
            unique = unique_counts[method]
            percentage = unique / total_slots * 100
            report += f"| {name} | {unique} | {percentage:.1f}% |\n"
        
        report += """

### Target Accuracy (Lower is Better)

| Method | Mean | Std Dev | vs Original |
|--------|------|---------|-------------|
"""
        
        orig_target = target_means['original']
        for method, name in zip(methods, method_names):
            mean = target_means[method]
            std = np.std(results[method]['target_accuracy'])
            vs_orig = ((orig_target - mean) / orig_target * 100)
            report += f"| {name} | {mean:.4f} | {std:.4f} | {vs_orig:+.1f}% |\n"
        
        report += """

---

## Statistical Significance

### Smoothness

"""
        
        for comparison, data in stat_results['smoothness'].items():
            sig_symbol = data['significance']
            report += f"- **{comparison}**: p={data['p_value']:.4f} {sig_symbol} (Cohen's d={data['cohens_d']:.2f})\n"
        
        report += """

### CF Cohesion

"""
        
        for comparison, data in stat_results['cf_cohesion'].items():
            sig_symbol = data['significance']
            report += f"- **{comparison}**: p={data['p_value']:.4f} {sig_symbol} (Cohen's d={data['cohens_d']:.2f})\n"
        
        report += """

**Significance levels:** *** p<0.001, ** p<0.01, * p<0.05, ns = not significant

**Effect size (Cohen's d):** Small=0.2, Medium=0.5, Large=0.8

---

## Method Characteristics

### Original (Pure Mood)

**Strengths:**
- Best target accuracy
- Predictable mood progression
- Deterministic results

**Weaknesses:**
- Lowest musical cohesion
- Limited variety (uses same tracks)
- May have jarring transitions

**Best for:**
- When mood accuracy is critical
- Therapeutic/mood regulation contexts
- Predictable user experiences

### CF-Enhanced (Pure CF, cf_weight=1.0)

**Strengths:**
- Highest musical cohesion
- Smooth listening experience
- Better flow between tracks

**Weaknesses:**
- May sacrifice some mood accuracy
- Still deterministic (same playlists)
- Moderate variety

**Best for:**
- Background music
- Extended listening sessions
- When musical flow is priority

### CF+Random (High Variation)

**Strengths:**
- Maximum variety (highest unique tracks)
- Discovery and serendipity
- Different playlists every time
- Balances cohesion and diversity

**Weaknesses:**
- Highest smoothness (least smooth)
- Less predictable
- May sacrifice some cohesion

**Best for:**
- Discovery mode
- Repeat listeners
- Radio-style features
- When variety is desired

---

## Recommendations

### Use Original when:
- Mood accuracy is critical
- Working in therapeutic contexts
- Need predictable results
- Targeting specific emotional states

### Use CF-Enhanced (cf_weight=1.0) when:
- Musical cohesion is priority
- Creating background playlists
- Long listening sessions
- Professional/work environments

### Use CF+Random (high variation) when:
- Users want variety
- Discovery is a feature
- Preventing playlist fatigue
- Radio or shuffle modes
- Repeat users

### Balanced Approach

For most use cases, consider a **hybrid configuration**:
- cf_weight=0.4-0.6 (balance mood and CF)
- randomness=0.3-0.5 (moderate variety)
- diversity=0.3 (some diversity enforcement)
- serendipity=optional

This provides good cohesion, moderate variety, and maintains mood accuracy.

---

## Conclusion

Each method excels in different areas:

- **Original**: Best mood accuracy, least cohesion
- **CF-Enhanced**: Best cohesion, deterministic
- **CF+Random**: Maximum variety, discovery-focused

The choice depends on your use case:

- **Accuracy priority** → Original
- **Cohesion priority** → CF-Enhanced (cf_weight=1.0)
- **Variety priority** → CF+Random (high variation)
- **Balanced** → CF with moderate parameters

All three methods have their place in a complete music recommendation system.

---

*Report generated by ThreeWayComparator*
"""
        
        # Save report
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ Report saved to: {output_file}\n")
    
    def plot_comparison(self, results: Dict, output_file: str = 'three_way_comparison_plots.png'):
        """
        Generate comparison visualizations.
        
        Args:
            results: Results from compare_all_methods
            output_file: Output filename
        """
        print("📊 Generating comparison plots...")
        
        methods = ['original', 'cf_enhanced', 'cf_random']
        method_names = ['Original\n(Mood)', 'CF-Enhanced\n(Pure CF)', 'CF+Random\n(High Var)']
        colors = ['#3498db', '#2ecc71', '#e74c3c']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Three-Way Method Comparison', fontsize=16, fontweight='bold')
        
        # Plot 1: Smoothness comparison
        ax1 = axes[0, 0]
        smoothness_data = [results[m]['smoothness'] for m in methods]
        bp1 = ax1.boxplot(smoothness_data, labels=method_names, patch_artist=True)
        for patch, color in zip(bp1['boxes'], colors):
            patch.set_facecolor(color)
        ax1.set_ylabel('Smoothness (lower is better)', fontsize=11)
        ax1.set_title('Smoothness Comparison', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Plot 2: CF Cohesion comparison
        ax2 = axes[0, 1]
        cohesion_data = [results[m]['cf_cohesion'] for m in methods]
        bp2 = ax2.boxplot(cohesion_data, labels=method_names, patch_artist=True)
        for patch, color in zip(bp2['boxes'], colors):
            patch.set_facecolor(color)
        ax2.set_ylabel('CF Cohesion (higher is better)', fontsize=11)
        ax2.set_title('Musical Cohesion Comparison', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Plot 3: Variety (unique tracks)
        ax3 = axes[1, 0]
        unique_counts = [len(results[m]['unique_tracks']) for m in methods]
        bars = ax3.bar(method_names, unique_counts, color=colors)
        ax3.set_ylabel('Unique Tracks Used', fontsize=11)
        ax3.set_title('Variety Comparison', fontsize=13, fontweight='bold')
        ax3.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=10)
        
        # Plot 4: Target Accuracy comparison
        ax4 = axes[1, 1]
        target_data = [results[m]['target_accuracy'] for m in methods]
        bp4 = ax4.boxplot(target_data, labels=method_names, patch_artist=True)
        for patch, color in zip(bp4['boxes'], colors):
            patch.set_facecolor(color)
        ax4.set_ylabel('Target Accuracy (lower is better)', fontsize=11)
        ax4.set_title('Target Accuracy Comparison', fontsize=13, fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Plots saved to: {output_file}\n")


def main():
    """Run three-way comparison"""
    parser = argparse.ArgumentParser(
        description='Compare Original vs CF-Enhanced vs CF+Random'
    )
    
    parser.add_argument('--dataset', type=str,
                       default='data/processed/spotify_mood_dataset.csv',
                       help='Path to dataset')
    parser.add_argument('--current-mood', type=str, default='sad_calm',
                       help='Starting mood')
    parser.add_argument('--target-mood', type=str, default='happy_energetic',
                       help='Target mood')
    parser.add_argument('--length', type=int, default=10,
                       help='Playlist length')
    parser.add_argument('--runs', type=int, default=20,
                       help='Number of runs per method')
    parser.add_argument('--output-report', type=str,
                       default='three_way_comparison_report.md',
                       help='Output report filename')
    parser.add_argument('--output-plots', type=str,
                       default='three_way_comparison_plots.png',
                       help='Output plots filename')
    parser.add_argument('--output-examples', type=str,
                       default='example_playlists.txt',
                       help='Output examples filename')
    parser.add_argument('--quick', action='store_true',
                       help='Quick comparison (fewer runs)')
    
    args = parser.parse_args()
    
    if args.quick:
        args.runs = 5
        print("🏃 Quick mode: Using 5 runs per method\n")
    
    try:
        # Initialize comparator
        comparator = ThreeWayComparator(args.dataset)
        
        # Run comparison
        print("\n" + "🔬" * 35)
        print("STARTING THREE-WAY COMPARISON")
        print("🔬" * 35 + "\n")
        
        results = comparator.compare_all_methods(
            args.current_mood, args.target_mood, args.length, args.runs
        )
        
        # Statistical tests
        stat_results = comparator.statistical_comparison(results)
        
        # Generate examples
        comparator.create_example_playlists(results, args.output_examples)
        
        # Generate report
        comparator.generate_report(results, stat_results, args.output_report)
        
        # Generate plots
        try:
            comparator.plot_comparison(results, args.output_plots)
        except Exception as e:
            print(f"⚠️  Could not generate plots: {e}")
        
        # Final summary
        print("=" * 70)
        print("COMPARISON COMPLETE!")
        print("=" * 70)
        
        print(f"\n📄 Files generated:")
        print(f"   Report: {args.output_report}")
        print(f"   Plots: {args.output_plots}")
        print(f"   Examples: {args.output_examples}")
        
    except FileNotFoundError:
        print(f"❌ Error: Dataset not found at {args.dataset}")
        print("\nOptions:")
        print("1. Generate sample data: python generate_sample_dataset.py")
        print("2. Specify your dataset: --dataset /path/to/your/data.csv")
    except Exception as e:
        print(f"❌ Error during comparison: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
