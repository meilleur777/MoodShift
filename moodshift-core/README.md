# 🎵 MoodShift Core - Mood-Based Music Recommendation System

The main recommendation engine for MoodShift that generates mood-transitioning playlists.

## 🌟 Features

- **Mood Classification**: Automatically classifies songs based on valence (happiness) and energy
- **Path Generation**: Creates smooth transitions between mood states
- **Collaborative Filtering**: Provides personalized recommendations based on track similarity
- **Flexible Algorithms**: Choose between greedy (fast) or smooth (better) path generation

## 📁 Structure

```
moodshift-core/
├── models/
│   ├── __init__.py
│   ├── mood_classifier.py          # Mood classification using Russell's model
│   ├── path_generator.py           # Playlist path generation
│   └── collaborative_filtering.py  # Track similarity recommendations
├── config.py                        # Configuration settings
├── main.py                          # Main CLI interface
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

1. Python 3.8 or higher
2. Required packages:
```bash
pip install pandas numpy scikit-learn scipy
```

3. Music dataset (from data collector):
   - Place `spotify_mood_dataset.csv` in `../data/processed/`

### Basic Usage

```bash
# Generate a playlist from sad to happy
python main.py --current-mood sad_calm --target-mood happy_energetic --length 10

# Use greedy algorithm (faster)
python main.py --current-mood neutral --target-mood happy_energetic --method greedy

# Save to custom file
python main.py --current-mood sad_calm --target-mood happy_calm --output my_playlist.csv
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--dataset` | Path to music dataset | `../data/processed/spotify_mood_dataset.csv` |
| `--current-mood` | Starting mood | `sad_calm` |
| `--target-mood` | Desired mood | `happy_energetic` |
| `--length` | Number of songs | `10` |
| `--method` | Algorithm (`smooth` or `greedy`) | `smooth` |
| `--output` | Output filename | `moodshift_playlist.csv` |

### Available Moods

- `happy_energetic` - Upbeat, exciting, joyful (high valence, high energy)
- `happy_calm` - Peaceful, content, serene (high valence, low energy)
- `sad_calm` - Melancholic, gentle, reflective (low valence, low energy)
- `sad_energetic` - Intense, angry, aggressive (low valence, high energy)
- `neutral` - Balanced, moderate (medium valence and energy)

## 💻 Python API Usage

### Example 1: Basic Playlist Generation

```python
from main import MoodShift

# Initialize
moodshift = MoodShift('../data/processed/spotify_mood_dataset.csv')

# Create playlist
playlist = moodshift.create_playlist(
    current_mood='sad_calm',
    target_mood='happy_energetic',
    length=10,
    method='smooth'
)

# Display
print(playlist[['name', 'artist', 'mood', 'valence', 'energy']])

# Save
moodshift.save_playlist(playlist, 'my_playlist.csv')
```

### Example 2: Using Individual Components

#### Mood Classifier

```python
from models.mood_classifier import MoodClassifier
import pandas as pd

# Load data
df = pd.read_csv('../data/processed/spotify_mood_dataset.csv')

# Initialize classifier
classifier = MoodClassifier()

# Classify a track
mood = classifier.classify(valence=0.8, energy=0.7)
print(f"Mood: {mood}")  # Output: happy_energetic

# Find tracks for a specific mood
happy_tracks = classifier.find_closest_tracks(
    df,
    target_valence=0.8,
    target_energy=0.7,
    n=10
)
```

#### Path Generator

```python
from models.path_generator import PathGenerator
import pandas as pd

# Load data
df = pd.read_csv('../data/processed/spotify_mood_dataset.csv')

# Initialize
generator = PathGenerator(df)

# Generate smooth path
path = generator.generate_path_smooth(
    start_mood='sad_calm',
    target_mood='happy_energetic',
    length=10,
    smoothness=0.7
)

# Check smoothness
smoothness = generator.calculate_path_smoothness(path)
print(f"Smoothness: {smoothness:.3f}")
```

#### Collaborative Filtering

```python
from models.collaborative_filtering import CollaborativeFilter
import pandas as pd

# Load data
df = pd.read_csv('../data/processed/spotify_mood_dataset.csv')

# Initialize
cf = CollaborativeFilter(df)

# Find similar tracks
similar = cf.get_similar_tracks('track_id_here', n=5)

# Recommend by features
recommendations = cf.recommend_by_features(
    target_features={
        'valence': 0.8,
        'energy': 0.7,
        'danceability': 0.8
    },
    n=10
)

# Diversify
diversified = cf.diversify_recommendations(
    recommendations,
    diversity_weight=0.3
)
```

## 🎯 How It Works

### 1. Mood Classification (Russell's Circumplex Model)

```
    Energy
      ↑
  1.0 |  Tense/Angry  |  Happy/Energetic
      |               |
  0.5 |----------Neutral-----------
      |               |
  0.0 |   Sad/Calm    |  Peaceful/Content
      |_______________|_____________→
     0.0             0.5           1.0
                 Valence
```

Tracks are classified based on two dimensions:
- **Valence**: Musical positivity (0 = sad, 1 = happy)
- **Energy**: Intensity and activity (0 = calm, 1 = energetic)

### 2. Path Generation Algorithms

#### Greedy Algorithm (Fast)
- Calculates direct path from start to target
- Divides path into equal steps
- Finds nearest track to each step
- **Pros**: Fast, simple
- **Cons**: May have larger mood jumps

#### Smooth Algorithm (Better)
- Balances smoothness with progress toward target
- Minimizes mood distance between consecutive songs
- Uses weighted scoring (smoothness vs. progress)
- **Pros**: More natural transitions
- **Cons**: Slower computation

### 3. Collaborative Filtering

- Builds similarity matrix using audio features
- Uses cosine similarity for track comparison
- Can diversify recommendations to avoid repetition
- Supports feature-based recommendations

## 📊 Evaluation Metrics

### Smoothness Score
Average mood distance between consecutive songs:
```python
smoothness = mean([distance(song[i], song[i+1]) for i in range(len(playlist)-1)])
```
- Lower is better
- Typical range: 0.05 - 0.30
- < 0.15 = Very smooth
- 0.15-0.25 = Smooth
- > 0.25 = Choppy

### Target Accuracy
Distance between final song and target mood:
```python
accuracy = distance(final_song_mood, target_mood_center)
```
- Lower is better
- < 0.2 = Excellent
- 0.2-0.4 = Good
- > 0.4 = Poor

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Mood classification thresholds
MOOD_SETTINGS = {
    'valence_threshold': 0.5,
    'energy_threshold': 0.5
}

# Path generation
PATH_SETTINGS = {
    'max_mood_jump': 0.25,
    'smoothness_weight': 0.7
}

# Collaborative filtering
CF_SETTINGS = {
    'diversity_weight': 0.3,
    'feature_weights': {
        'valence': 1.5,
        'energy': 1.5,
        # ...
    }
}
```

## 🔬 Advanced Usage

### Custom Mood Definitions

```python
from models.mood_classifier import MoodClassifier

classifier = MoodClassifier(
    valence_threshold=0.6,  # Stricter happiness threshold
    energy_threshold=0.4    # Lower energy threshold
)
```

### Adjust Path Smoothness

```python
from models.path_generator import PathGenerator

generator = PathGenerator(df, max_mood_jump=0.15)  # Stricter jumps

path = generator.generate_path_smooth(
    start_mood='sad_calm',
    target_mood='happy_energetic',
    length=15,
    smoothness=0.9  # Very smooth (vs. 0.5 = more direct)
)
```

### Feature-Weighted Recommendations

```python
from models.collaborative_filtering import CollaborativeFilter
from sklearn.preprocessing import StandardScaler

# Initialize with custom weights
cf = CollaborativeFilter(df)

# Recommend with emphasis on specific features
recommendations = cf.recommend_by_features(
    target_features={
        'valence': 0.8,
        'energy': 0.7,
        'danceability': 0.9,  # Emphasize danceability
        'acousticness': 0.1   # Avoid acoustic
    },
    n=10
)
```

## 🧪 Testing

Each module has a `main()` function for testing:

```bash
# Test mood classifier
cd models
python mood_classifier.py

# Test path generator
python path_generator.py

# Test collaborative filtering
python collaborative_filtering.py
```

## 📈 Performance

Typical performance on a dataset of 500-1000 tracks:

| Operation | Time | Memory |
|-----------|------|--------|
| Load dataset | < 1s | ~10 MB |
| Build similarity matrix | 1-3s | ~50 MB |
| Generate playlist (10 songs) | < 1s | Minimal |
| Find similar tracks | < 0.1s | Minimal |

## 🐛 Troubleshooting

### "No tracks found for mood"
- Your dataset might not have enough tracks in that mood range
- Try using `neutral` as start or target mood
- Collect more diverse data

### "Playlist is choppy/not smooth"
- Increase playlist length (more intermediate songs)
- Increase `smoothness` parameter (0.9 for very smooth)
- Decrease `max_mood_jump` in config

### "Recommendations are too similar"
- Increase `diversity_weight` (try 0.5 or 0.7)
- Use larger dataset with more variety

## 🎓 References

- Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*
- Spotify Audio Features: https://developer.spotify.com/documentation/web-api/reference/get-audio-features
- Collaborative Filtering: Koren, Y., Bell, R., & Volinsky, C. (2009). Matrix factorization techniques for recommender systems

---

[← Back to Main Project](../README.md)
