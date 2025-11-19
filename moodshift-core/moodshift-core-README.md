# 🎵 MoodShift Core

The main recommendation engine that generates mood-transitioning playlists using collaborative filtering and path-finding algorithms.

## 🎯 Purpose

The MoodShift core system:
- Implements collaborative filtering for personalized recommendations
- Classifies songs into mood categories based on audio features
- Generates optimal paths through mood space
- Creates smooth transitions between emotional states

## 📁 Structure

```
moodshift-core/
├── models/
│   ├── collaborative_filtering.py   # CF recommendation models
│   ├── mood_classifier.py          # Mood classification
│   └── path_generator.py           # Playlist path generation
├── utils/
│   ├── preprocessing.py            # Data preprocessing utilities
│   └── feature_extraction.py      # Feature engineering
├── main.py                         # CLI interface
├── config.py                       # Configuration settings
└── README.md                       # This file
```

## 🚀 Quick Start

### Prerequisites

1. Collected music dataset (see [data-collector](../data-collector/README.md))
2. Python 3.8+
3. Required dependencies installed

### Installation

```bash
# From project root
pip install -r requirements.txt
```

### Basic Usage

```bash
python main.py --current-mood "sad" --target-mood "happy" --length 10
```

**Parameters:**
- `--current-mood`: Starting emotional state (sad, happy, calm, energetic, neutral)
- `--target-mood`: Desired emotional state
- `--length`: Number of songs in the playlist (default: 10)
- `--user-id`: Optional user ID for personalized recommendations

## 🤖 Models

### 1. Collaborative Filtering

#### Item-Based Collaborative Filtering

Recommends songs based on similarity to songs the user has liked:

```python
from models.collaborative_filtering import ItemBasedCF

model = ItemBasedCF(n_neighbors=20)
model.fit(user_item_matrix)
recommendations = model.recommend(user_id, n_items=10)
```

#### Matrix Factorization (SVD)

Uses singular value decomposition for latent factor models:

```python
from models.collaborative_filtering import MatrixFactorizationCF

model = MatrixFactorizationCF(n_factors=50)
model.fit(user_item_matrix)
predictions = model.predict(user_id, item_id)
```

**Advantages:**
- Personalized to user preferences
- Handles sparse data well
- Discovers latent patterns

### 2. Mood Classifier

Maps audio features to mood categories:

```python
from models.mood_classifier import MoodClassifier

classifier = MoodClassifier()
classifier.fit(tracks_df)

# Classify a song
mood = classifier.predict(audio_features)  # Returns: 'happy_energetic', 'sad_calm', etc.

# Get mood scores
scores = classifier.predict_proba(audio_features)
```

**Mood Space:**
- Based on valence (happiness) and energy (activity)
- Creates 4-5 distinct mood zones
- Uses weighted audio features

### 3. Path Generator

Creates smooth transitions between moods:

```python
from models.path_generator import PathGenerator

generator = PathGenerator(dataset)
playlist = generator.generate_path(
    start_mood='sad_calm',
    target_mood='happy_energetic',
    length=10,
    user_id=123  # Optional for personalization
)
```

**Algorithm:**
1. Find songs near current mood
2. Find songs near target mood
3. Use A* or Dijkstra to find optimal path
4. Minimize mood distance between consecutive songs
5. Consider user preferences (if available)

## 🔧 Configuration

Edit `config.py` to customize:

```python
# Mood thresholds
VALENCE_THRESHOLD = 0.5
ENERGY_THRESHOLD = 0.5

# Path generation
MAX_MOOD_DISTANCE = 0.3  # Maximum allowed jump between songs
MIN_PLAYLIST_LENGTH = 5
MAX_PLAYLIST_LENGTH = 50

# Collaborative filtering
N_FACTORS = 50
N_NEIGHBORS = 20
MIN_USER_INTERACTIONS = 5
```

## 📊 Mood Space

The system uses a 2D mood space:

```
    Energy
      ↑
  1.0 |  Angry/Tense  |  Happy/Energetic
      |               |
  0.5 |---------------------------- 
      |               |
  0.0 |   Sad/Calm    |  Peaceful/Content
      |_______________|_________________→
     0.0             0.5              1.0  Valence
```

**Mood Categories:**

| Category | Valence | Energy | Examples |
|----------|---------|--------|----------|
| `happy_energetic` | High (>0.6) | High (>0.6) | Dance, Pop, Upbeat |
| `happy_calm` | High (>0.6) | Low (<0.4) | Acoustic, Folk, Gentle |
| `sad_calm` | Low (<0.4) | Low (<0.4) | Ballad, Ambient, Melancholy |
| `tense_energetic` | Low (<0.4) | High (>0.6) | Rock, Metal, Intense |
| `neutral` | Mid (0.4-0.6) | Mid (0.4-0.6) | Balanced tracks |

## 🛤️ Path Generation Strategies

### Strategy 1: Direct Path (Fastest)

Shortest path through mood space:
- Minimizes number of transitions
- May have larger mood jumps
- Best for quick mood changes

### Strategy 2: Smooth Path (Default)

Gradual transitions with small steps:
- Maximizes smoothness between songs
- More natural listening experience
- Longer playlists for distant moods

### Strategy 3: Scenic Path

Explores multiple emotional states:
- Takes interesting detours
- Exposes user to varied music
- Best for discovery

## 📈 Evaluation Metrics

The system tracks:

### Transition Smoothness
```python
smoothness = average([distance(song_i, song_i+1) for i in range(len(playlist)-1)])
```
- Lower is better
- Typical: 0.1-0.3

### Target Accuracy
```python
accuracy = distance(final_song_mood, target_mood)
```
- Lower is better
- Good: <0.2

### User Satisfaction
- Collected through user feedback
- Rated 1-5 stars
- Tracks skip rate

## 🔬 Advanced Usage

### Custom Mood Weights

Weight different features for mood calculation:

```python
from models.mood_classifier import MoodClassifier

classifier = MoodClassifier(
    valence_weight=0.6,
    energy_weight=0.3,
    tempo_weight=0.1
)
```

### Personalized Paths

Include user history for better recommendations:

```python
generator = PathGenerator(
    dataset,
    use_collaborative_filtering=True,
    cf_weight=0.3  # Balance CF vs. mood-based
)

playlist = generator.generate_path(
    start_mood='sad',
    target_mood='happy',
    user_id=123
)
```

### Constraint-Based Generation

Add constraints to path generation:

```python
playlist = generator.generate_path(
    start_mood='sad',
    target_mood='happy',
    constraints={
        'min_tempo': 80,
        'max_tempo': 140,
        'exclude_artists': ['Artist1', 'Artist2'],
        'prefer_decades': [2010, 2020]
    }
)
```

## 🧪 Testing

Run unit tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=models tests/
```

## 🐛 Troubleshooting

### "No path found" error
- Moods may be too far apart for playlist length
- Increase `--length` parameter
- Check if dataset has intermediate mood songs

### Poor recommendations
- Dataset may be too small (<500 tracks)
- User may need more interaction history
- Adjust CF weights in config

### Slow performance
- Reduce dataset size for testing
- Use simpler path algorithm
- Cache computed similarities

## 🚧 TODO

- [ ] Implement user feedback loop
- [ ] Add real-time mood adjustment
- [ ] Export playlists to Spotify
- [ ] Web API for integration
- [ ] Support for custom mood definitions
- [ ] Multi-objective optimization (mood + diversity + familiarity)

## 📚 References

- [Collaborative Filtering Overview](https://en.wikipedia.org/wiki/Collaborative_filtering)
- [Music Emotion Recognition](https://www.ismir.net/)
- [Graph Algorithms](https://networkx.org/)

---

[← Back to Main README](../README.md) | [Data Collector →](../data-collector/README.md)
