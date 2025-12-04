# 🎵 MoodShift

**Intelligent Music Recommendation System for Emotional Well-being**

MoodShift is an advanced music recommendation system that creates personalized playlists designed to gradually transition your emotional state. Unlike traditional mood-matching systems that simply play songs that match your current mood, MoodShift guides you from your current emotional state to your desired target state through carefully curated musical journeys.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🌟 Key Features

### 🎯 Mood-Based Transitions
- **Russell's Circumplex Model**: Maps songs across two emotional dimensions (valence and energy)
- **Smooth Pathfinding**: Creates gradual transitions between emotional states
- **5 Mood Categories**: Happy-Energetic, Happy-Calm, Sad-Calm, Sad-Energetic, and Neutral

### 🤝 Collaborative Filtering
- **Musical Cohesion**: Ensures tracks flow naturally together
- **Similarity Analysis**: Uses audio features to find musically compatible songs
- **Hybrid Scoring**: Balances mood progression with musical similarity

### 🎲 Randomization & Variety
- **Configurable Randomness**: Control playlist variety (0.0 = deterministic, 1.0 = highly varied)
- **Diversity Enforcement**: Prevents repetitive track selection
- **Serendipity Mode**: Enables unexpected musical discoveries

### 📊 Data-Driven
- **Spotify Integration**: Leverages Spotify's audio feature API
- **8+ Audio Features**: Valence, energy, danceability, tempo, acousticness, and more
- **Comprehensive Analysis**: Dataset statistics and visualization tools

---

## 🏗️ Architecture

```
moodshift/
├── data-collector/          # Spotify API data collection
│   ├── collector.py        # Main data collection script
│   ├── analyzer.py         # Dataset analysis & visualization
│   └── README.md           # Data collection documentation
│
├── moodshift-core/         # Core recommendation engine
│   ├── models/
│   │   ├── mood_classifier.py           # Mood classification
│   │   ├── path_generator.py            # Path generation algorithms
│   │   ├── path_generator_cf.py         # CF-enhanced path generation
│   │   ├── path_generator_cf_random.py  # Randomized path generation
│   │   └── collaborative_filtering.py   # Track similarity engine
│   │
│   ├── main.py             # Original mood-based system
│   ├── main_cf.py          # CF-enhanced system
│   ├── main_cf_random.py   # CF with randomization
│   └── README.md           # Core system documentation
│
└── data/                   # Dataset storage
    ├── raw/                # Raw Spotify data
    └── processed/          # Processed datasets
```

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8 or higher
python --version

# Required packages
pip install pandas numpy scikit-learn scipy spotipy matplotlib seaborn python-dotenv
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/moodshift.git
cd moodshift
```

2. **Set up Spotify API credentials**

Create a `.env` file in the project root:
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Get your credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

3. **Collect music data**
```bash
cd data-collector
pip install -r Requirements.txt
python ultra_simple_collector.py
```

This will create `spotify_mood_dataset.csv` with ~500-800 tracks.

4. **Generate your first playlist**
```bash
cd ../moodshift-core
python main_cf_random.py \
  --current-mood sad_calm \
  --target-mood happy_energetic \
  --length 10 \
  --randomness 0.4
```

---

## 📖 Usage Examples

### Basic Playlist Generation

```python
from main_cf_random import MoodShiftCF

# Initialize system
ms = MoodShiftCF('data/processed/spotify_mood_dataset.csv')

# Create a mood-transitioning playlist
playlist = ms.create_playlist(
    current_mood='sad_calm',
    target_mood='happy_energetic',
    length=10,
    method='cf_enhanced',
    cf_weight=0.4,           # Balance mood vs musical similarity
    randomness=0.4,          # Add variety
    diversity_weight=0.3,    # Avoid repetition
    serendipity=True         # Enable discoveries
)

# Save playlist
ms.save_playlist(playlist, 'my_playlist.csv')
```

### Command Line Interface

```bash
# Generate a calming playlist
python main_cf_random.py \
  --current-mood sad_energetic \
  --target-mood happy_calm \
  --length 15 \
  --cf-weight 0.5 \
  --randomness 0.3

# High-variety discovery mode
python main_cf_random.py \
  --current-mood neutral \
  --target-mood happy_energetic \
  --randomness 0.7 \
  --diversity 0.5 \
  --serendipity

# Reproducible playlist (same seed = same result)
python main_cf_random.py \
  --current-mood sad_calm \
  --target-mood happy_energetic \
  --seed 42
```

---

## 🎭 Mood Categories

MoodShift uses **Russell's Circumplex Model** to map emotional states:

```
         Energy (Intensity)
              ↑
          1.0 |
              |
    Sad/      |      Happy/
    Angry  ---|---  Energetic
              |
    0.5  ─────┼─────  Neutral
              |
    Sad/      |      Happy/
    Calm   ---|---    Calm
              |
          0.0 |
              └──────────────→
             0.0    0.5    1.0
                  Valence (Happiness)
```

### Available Moods

| Mood | Valence | Energy | Description | Use Cases |
|------|---------|--------|-------------|-----------|
| **happy_energetic** | High (0.6-1.0) | High (0.6-1.0) | Upbeat, exciting, joyful | Workouts, parties, motivation |
| **happy_calm** | High (0.6-1.0) | Low (0.0-0.4) | Peaceful, content, serene | Relaxation, focus work, meditation |
| **sad_calm** | Low (0.0-0.4) | Low (0.0-0.4) | Melancholic, gentle, reflective | Contemplation, emotional processing |
| **sad_energetic** | Low (0.0-0.4) | High (0.6-1.0) | Intense, angry, aggressive | Catharsis, intense workouts |
| **neutral** | Medium (0.4-0.6) | Medium (0.4-0.6) | Balanced, moderate | Background music, studying |

---

## 🔬 Technical Deep Dive

### Mood Classification

MoodShift classifies songs using two primary dimensions from Spotify's audio features:

- **Valence (0-1)**: Musical positivity/happiness
- **Energy (0-1)**: Intensity and activity level

```python
def classify(valence: float, energy: float) -> str:
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
```

### Path Generation Algorithms

#### 1. **Smooth Path Generation** (Original)
- Calculates ideal trajectory from start to target
- Finds nearest tracks to ideal points
- Balances smoothness vs. progress

#### 2. **CF-Enhanced Path** (Improved)
- Combines mood-based selection with collaborative filtering
- Uses track similarity to improve musical flow
- Adjustable `cf_weight` parameter (0-1)

**Scoring Formula:**
```
final_score = (1 - cf_weight) × mood_score + cf_weight × cf_score
```

#### 3. **Randomized Path** (Latest)
- Adds probabilistic selection for variety
- Temperature-based sampling
- Diversity enforcement to avoid repetition
- Optional serendipity for unexpected discoveries

### Collaborative Filtering

MoodShift uses **item-based collaborative filtering** with cosine similarity:

```python
# Audio features used for similarity
features = [
    'valence', 'energy', 'danceability', 
    'acousticness', 'instrumentalness', 
    'speechiness', 'tempo', 'loudness'
]

# Normalize and calculate similarity
features_normalized = StandardScaler().fit_transform(features)
similarity_matrix = cosine_similarity(features_normalized)
```

**Benefits:**
- Ensures musically cohesive transitions
- Discovers tracks users might enjoy
- Improves playlist listening experience

---

## 📊 Evaluation & Performance

### Metrics

MoodShift tracks four key metrics:

1. **Smoothness** (lower is better)
   - Average mood distance between consecutive tracks
   - Target: < 0.15 (very smooth)

2. **CF Cohesion** (higher is better)
   - Average similarity between consecutive tracks
   - Target: > 0.7 (high cohesion)

3. **Variety** (moderate is optimal)
   - Standard deviation of mood features
   - Balanced approach preferred

4. **Target Accuracy** (lower is better)
   - Distance from final track to target mood
   - Target: < 0.2 (excellent)

### Method Comparison

| Method | Smoothness | CF Cohesion | Variety | Best For |
|--------|-----------|-------------|---------|----------|
| **Original** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Mood accuracy |
| **CF-Enhanced** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Musical flow |
| **CF+Random** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Discovery & variety |

**Recommendations:**
- **Therapeutic use**: Original method (mood accuracy priority)
- **Background music**: CF-Enhanced with `cf_weight=0.7`
- **Active listening**: CF+Random with `randomness=0.4-0.5`
- **Discovery mode**: CF+Random with `randomness=0.7`, `diversity=0.5`, `serendipity=True`

---

## 🛠️ Configuration

### Optimal Settings

**Balanced (Recommended for most users):**
```python
cf_weight = 0.4
randomness = 0.4
diversity_weight = 0.3
serendipity = True
```

**Mood-Focused (Therapeutic/Clinical):**
```python
cf_weight = 0.2
randomness = 0.0
diversity_weight = 0.0
serendipity = False
```

**Discovery Mode (Maximum variety):**
```python
cf_weight = 0.5
randomness = 0.7
diversity_weight = 0.5
serendipity = True
```

**Background/Work Music:**
```python
cf_weight = 0.7
randomness = 0.2
diversity_weight = 0.2
serendipity = False
```

---

## 📈 Dataset

### Collection

The system uses the Spotify Web API to collect track data:

```bash
cd data-collector
python ultra_simple_collector.py
```

**Collected Features:**
- Track metadata (name, artist, album)
- Audio features (valence, energy, danceability, tempo, etc.)
- Popularity and duration
- Mood classification

### Analysis

Analyze your dataset:

```bash
cd data-collector
python analyzer.py
```

Generates:
- Mood distribution statistics
- Feature correlation heatmaps
- Tempo distribution plots
- Mood space visualization

### Dataset Requirements

**Minimum:**
- 500 tracks
- Coverage across all 5 mood categories
- Complete audio features

**Recommended:**
- 1,000+ tracks
- Diverse genres and artists
- Balanced mood distribution

---

## 🧪 Testing & Evaluation

### Run Tests

```bash
cd moodshift-core
python test_cf_implementation.py
```

### Evaluate CF Weight

Find optimal collaborative filtering weight:

```bash
python evaluate_cf_weight.py --runs 10
```

### Evaluate Randomization

Test different randomness levels:

```bash
python evaluate_cf_random.py --runs 10
```

### Compare Methods

Three-way comparison (Original vs CF vs CF+Random):

```bash
python compare_three_methods.py --runs 20
```

---

## 📚 Documentation

### Core Documentation

- **[Data Collector README](data-collector/README.md)**: Spotify API setup and data collection
- **[MoodShift Core README](moodshift-core/README.md)**: System architecture and algorithms
- **[CF Weight Evaluation Report](moodshift-core/cf_weight_evaluation_report.md)**: Optimal CF weight analysis
- **[CF Random Evaluation Report](moodshift-core/cf_random_evaluation_report.md)**: Randomization impact study
- **[Three-Way Comparison](moodshift-core/three_way_comparison_report.md)**: Method comparison report

### Academic References

1. **Russell, J. A. (1980)**. "A circumplex model of affect." *Journal of Personality and Social Psychology*, 39(6), 1161-1178.

2. **Spotify Audio Features Documentation**. https://developer.spotify.com/documentation/web-api/reference/get-audio-features

3. **Koren, Y., Bell, R., & Volinsky, C. (2009)**. "Matrix factorization techniques for recommender systems." *Computer*, 42(8), 30-37.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

### High Priority
- [ ] User preference learning
- [ ] Playlist export to Spotify
- [ ] Web interface
- [ ] Mobile app integration

### Medium Priority
- [ ] Genre-specific models
- [ ] Tempo-based transitions
- [ ] Multi-language support
- [ ] User feedback system

### Research Opportunities
- [ ] Deep learning mood prediction
- [ ] EEG-based mood validation
- [ ] Clinical effectiveness studies
- [ ] Long-term user studies

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

### Common Issues

**1. "Dataset not found" error**
```bash
# Generate a sample dataset
cd data-collector
python ultra_simple_collector.py
```

**2. Spotify API 403 errors**
- Wait 30-60 minutes (rate limit)
- Check credentials are correct
- Try creating a new Spotify app

**3. "No tracks found for mood"**
- Collect more diverse data
- Use broader mood categories
- Try different search terms in data collection

**4. Poor playlist quality**
- Increase dataset size (aim for 1,000+ tracks)
- Adjust `cf_weight` (try 0.3-0.5)
- Reduce `max_mood_jump` in config

### Performance Tips

- **Large datasets**: CF similarity matrix takes ~1-3 seconds for 1,000 tracks
- **Memory usage**: ~50 MB for 1,000 tracks
- **Playlist generation**: < 1 second for 10-song playlist

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Spotify Web API** for audio feature data
- **Russell's Circumplex Model** for emotional mapping framework
- **scikit-learn** for collaborative filtering algorithms
- **UC Berkeley CS188** for reinforcement learning foundations

---

## 📧 Contact

**Project Maintainer**: V

**Issues**: [GitHub Issues](https://github.com/yourusername/moodshift/issues)

**Email**: your.email@example.com

---

## 🗺️ Roadmap

### Version 1.0 (Current)
- ✅ Mood classification
- ✅ Path generation (smooth, greedy)
- ✅ Collaborative filtering
- ✅ Randomization & variety
- ✅ Comprehensive evaluation

### Version 1.1 (In Progress)
- 🔄 Web interface
- 🔄 Spotify playlist export
- 🔄 User feedback system

### Version 2.0 (Planned)
- 📋 User preference learning
- 📋 Real-time mood detection
- 📋 Social features (shared playlists)
- 📋 Advanced analytics dashboard

### Version 3.0 (Future)
- 💭 Deep learning models
- 💭 Multi-modal emotion detection
- 💭 Clinical integration
- 💭 Mobile applications

---

## 📊 Project Statistics

- **Lines of Code**: ~5,000+
- **Dataset Size**: 500-1,000 tracks (expandable)
- **Mood Categories**: 5
- **Audio Features**: 8+
- **Algorithms**: 3 (Original, CF-Enhanced, CF+Random)
- **Test Coverage**: Comprehensive evaluation suite

---

<div align="center">

**Built with ❤️ for emotional well-being through music**

[⭐ Star this repo](https://github.com/yourusername/moodshift) | [📖 Documentation](moodshift-core/README.md) | [🐛 Report Bug](https://github.com/yourusername/moodshift/issues)

</div>
