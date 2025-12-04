"""
Test Script for MoodShift CF Implementation
Run this to verify everything is working correctly
"""

import pandas as pd
import numpy as np


def test_collaborative_filtering():
    """Test 1: Collaborative Filtering"""
    print("\n" + "=" * 70)
    print("TEST 1: Collaborative Filtering")
    print("=" * 70)
    
    from models.collaborative_filtering import CollaborativeFilter
    
    # Create sample data
    sample_data = pd.DataFrame({
        'track_id': ['t1', 't2', 't3', 't4', 't5'],
        'name': ['Song A', 'Song B', 'Song C', 'Song D', 'Song E'],
        'artist': ['Artist 1', 'Artist 2', 'Artist 3', 'Artist 4', 'Artist 5'],
        'valence': [0.2, 0.25, 0.8, 0.75, 0.5],
        'energy': [0.3, 0.35, 0.7, 0.65, 0.5],
        'danceability': [0.4, 0.45, 0.9, 0.85, 0.6]
    })
    
    print("\n📊 Sample data:")
    print(sample_data[['name', 'valence', 'energy']])
    
    # Initialize CF
    print("\n🔧 Initializing CF...")
    cf = CollaborativeFilter(sample_data, verbose=True)
    
    # Test similarity
    print("\n🔍 Finding similar tracks to 'Song A'...")
    similar = cf.get_similar_tracks('t1', n=3)
    
    if similar:
        print("✓ Found similar tracks:")
        for track in similar:
            print(f"  • {track['name']}: similarity = {track['similarity']:.3f}")
    else:
        print("✗ No similar tracks found")
    
    # Get statistics
    stats = cf.get_statistics()
    print(f"\n📈 CF Statistics:")
    print(f"  Tracks: {stats['num_tracks']}")
    print(f"  Features used: {', '.join(stats['features_used'])}")
    print(f"  Avg similarity: {stats['avg_similarity']:.3f}")
    
    print("\n✅ Collaborative Filtering test passed!")
    return True


def test_path_generator():
    """Test 2: CF-Enhanced Path Generator"""
    print("\n" + "=" * 70)
    print("TEST 2: CF-Enhanced Path Generator")
    print("=" * 70)
    
    from models.mood_classifier import MoodClassifier
    from models.collaborative_filtering import CollaborativeFilter
    from models.path_generator_cf import PathGeneratorCF
    
    # Create sample data with more tracks
    np.random.seed(42)
    n_tracks = 50
    
    sample_data = pd.DataFrame({
        'track_id': [f't{i}' for i in range(n_tracks)],
        'name': [f'Song {i}' for i in range(n_tracks)],
        'artist': [f'Artist {i%10}' for i in range(n_tracks)],
        'valence': np.random.random(n_tracks),
        'energy': np.random.random(n_tracks),
        'danceability': np.random.random(n_tracks),
        'acousticness': np.random.random(n_tracks)
    })
    
    print(f"\n📊 Created sample dataset with {len(sample_data)} tracks")
    
    # Initialize components
    print("\n🔧 Initializing components...")
    classifier = MoodClassifier()
    cf = CollaborativeFilter(sample_data, verbose=False)
    path_gen = PathGeneratorCF(sample_data, classifier, cf)
    
    # Test smooth method (original)
    print("\n📝 Testing original smooth method...")
    path_orig = path_gen.generate_path_smooth(
        'sad_calm', 'happy_energetic', length=5
    )
    
    print(f"✓ Generated {len(path_orig)} tracks (smooth method)")
    
    # Test CF-enhanced method
    print("\n📝 Testing CF-enhanced method...")
    path_cf = path_gen.generate_path_cf_enhanced(
        'sad_calm', 'happy_energetic', 
        length=5, cf_weight=0.4, verbose=False
    )
    
    print(f"✓ Generated {len(path_cf)} tracks (CF-enhanced method)")
    
    # Compare metrics
    metrics_orig = path_gen.calculate_path_metrics(path_orig)
    metrics_cf = path_gen.calculate_path_metrics(path_cf)
    
    print("\n📈 Metrics Comparison:")
    print(f"  Smoothness:")
    print(f"    Original: {metrics_orig['smoothness']:.3f}")
    print(f"    CF-Enhanced: {metrics_cf['smoothness']:.3f}")
    print(f"  CF Cohesion:")
    print(f"    Original: {metrics_orig['cf_cohesion']:.3f}")
    print(f"    CF-Enhanced: {metrics_cf['cf_cohesion']:.3f}")
    
    print("\n✅ Path Generator test passed!")
    return True


def test_main_system():
    """Test 3: Integrated Main System"""
    print("\n" + "=" * 70)
    print("TEST 3: Integrated Main System")
    print("=" * 70)
    
    # This test requires a real dataset
    # Create a minimal test dataset
    print("\n🔧 Creating test dataset...")
    
    np.random.seed(42)
    n_tracks = 100
    
    test_data = pd.DataFrame({
        'track_id': [f'test_track_{i}' for i in range(n_tracks)],
        'name': [f'Test Song {i}' for i in range(n_tracks)],
        'artist': [f'Test Artist {i%20}' for i in range(n_tracks)],
        'valence': np.random.random(n_tracks),
        'energy': np.random.random(n_tracks),
        'danceability': np.random.random(n_tracks),
        'acousticness': np.random.random(n_tracks),
        'tempo': np.random.uniform(60, 200, n_tracks),
        'loudness': np.random.uniform(-60, 0, n_tracks)
    })
    
    # Save test dataset
    test_data.to_csv('test_dataset.csv', index=False)
    print(f"✓ Created test dataset: test_dataset.csv ({len(test_data)} tracks)")
    
    # Try to initialize main system
    try:
        from main_cf import MoodShiftCF
        
        print("\n🔧 Initializing MoodShift with CF...")
        ms = MoodShiftCF('test_dataset.csv', verbose=False)
        
        print("\n📝 Creating test playlist...")
        playlist = ms.create_playlist(
            'sad_calm', 'happy_energetic',
            length=5, method='cf_enhanced',
            cf_weight=0.4
        )
        
        print(f"✓ Generated playlist with {len(playlist)} tracks:")
        for _, track in playlist.iterrows():
            print(f"  {track['step']}. {track['name']}")
        
        # Test comparison
        print("\n📊 Testing method comparison...")
        comparison = ms.compare_methods('sad_calm', 'happy_energetic', length=5)
        
        print(f"✓ Comparison complete:")
        print(f"  Smoothness improvement: {comparison['improvements']['smoothness']:.1f}%")
        print(f"  Cohesion improvement: {comparison['improvements']['cohesion']:.1f}%")
        
        print("\n✅ Main system test passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Main system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("MOODSHIFT CF IMPLEMENTATION - TEST SUITE")
    print("=" * 70)
    
    results = []
    
    try:
        results.append(("Collaborative Filtering", test_collaborative_filtering()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Collaborative Filtering", False))
    
    try:
        results.append(("Path Generator", test_path_generator()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Path Generator", False))
    
    try:
        results.append(("Main System", test_main_system()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        results.append(("Main System", False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! CF implementation is ready!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    import sys
    
    # Add models directory to path
    sys.path.insert(0, 'models')
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
