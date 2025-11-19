# 🎵 MoodShift

A mood-based music recommendation system that creates personalized playlists to gradually transition your emotional state from your current mood to your desired mood.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Spotify API](https://img.shields.io/badge/Spotify-API-1DB954.svg)](https://developer.spotify.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🌟 Overview

MoodShift uses collaborative filtering and audio feature analysis to recommend sequences of songs that smoothly transition between emotional states. Instead of simply matching your current mood, MoodShift creates a musical journey that helps you reach your desired emotional destination.

### Key Features

- 🎯 **Mood-based transitions**: Gradual playlist generation from current to target mood
- 🎼 **Audio feature analysis**: Leverages Spotify's audio features (valence, energy, tempo, etc.)
- 🤝 **Collaborative filtering**: Personalized recommendations based on listening patterns
- 📊 **Data-driven**: Built on comprehensive music dataset with mood annotations
- 🔄 **Smooth pathfinding**: Intelligent song sequencing for natural emotional progression

## 🏗️ Project Structure

```
moodshift/
├── data-collector/          # Spotify data collection system
│   ├── collector.py
│   ├── analyzer.py
│   └── README.md
│
├── moodshift-core/          # Main recommendation system
│   ├── models/
│   │   ├── collaborative_filtering.py
│   │   ├── mood_classifier.py
│   │   └── path_generator.py
│   ├── utils/
│   │   ├── preprocessing.py
│   │   └── feature_extraction.py
│   └── README.md
│
├── data/                    # Datasets (not tracked in git)
│   ├── raw/
│   └── processed/
│
├── notebooks/               # Jupyter notebooks for experimentation
│   ├── data_exploration.ipynb
│   └── model_evaluation.ipynb
│
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md               # This file
```

## 🎯 How It Works

### 1. Mood Representation

MoodShift uses a two-dimensional mood space based on psychological research (Russell's Circumplex Model):

- **Valence** (X-axis): Musical positivity (0 = sad, 1 = happy)
- **Energy** (Y-axis): Intensity and activity (0 = calm, 1 = energetic)

This creates four primary mood quadrants:
- 🌞 **Happy & Energetic**: High valence, high energy
- 😌 **Happy & Calm**: High valence, low energy
- 😔 **Sad & Calm**: Low valence, low energy
- 😠 **Tense & Energetic**: Low valence, high energy

### 2. Recommendation Pipeline

```
User Input (Current Mood → Target Mood)
    ↓
Mood Classification (Map to audio features)
    ↓
Collaborative Filtering (Find relevant songs)
    ↓
Path Generation (Create smooth transition)
    ↓
Playlist Output (Ordered song sequence)
```

### 3. Path Generation Algorithm

The system finds the optimal path through mood space by:
1. Identifying songs near the current mood
2. Identifying songs near the target mood
3. Finding intermediate songs that create smooth transitions
4. Minimizing "mood distance" between consecutive songs
5. Ensuring playlist coherence and listenability

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Spotify Developer Account (free)
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/moodshift.git
cd moodshift
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Spotify API credentials:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Create a new app
   - Copy your Client ID and Client Secret
   - Create a `.env` file in the root directory:
```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### Quick Start

#### Step 1: Collect Data

```bash
cd data-collector
python collector.py --num-tracks 1000
```

This will collect songs across different mood categories and save them to `data/raw/`.

#### Step 2: Run MoodShift

```bash
cd moodshift-core
python main.py --current-mood "sad" --target-mood "happy" --length 10
```

This will generate a 10-song playlist transitioning from sad to happy.

## 📊 Dataset

### Audio Features

The system uses Spotify's audio features for each track:

| Feature | Range | Description |
|---------|-------|-------------|
| **valence** | 0.0 - 1.0 | Musical positivity/happiness |
| **energy** | 0.0 - 1.0 | Intensity and activity level |
| **danceability** | 0.0 - 1.0 | Suitability for dancing |
| **tempo** | 0 - 250 | Beats per minute (BPM) |
| **acousticness** | 0.0 - 1.0 | Likelihood of being acoustic |
| **instrumentalness** | 0.0 - 1.0 | Likelihood of no vocals |
| **speechiness** | 0.0 - 1.0 | Presence of spoken words |
| **loudness** | -60 - 0 | Overall loudness in decibels |
| **liveness** | 0.0 - 1.0 | Presence of live audience |
| **key** | 0 - 11 | Musical key (pitch class) |
| **mode** | 0 or 1 | Major (1) or minor (0) |

### Data Collection

See the [data-collector README](data-collector/README.md) for detailed information on collecting and preprocessing music data.

## 🤖 Models

### Collaborative Filtering

The system uses collaborative filtering to personalize recommendations based on:
- User listening history
- Similar users' preferences
- Item-item similarity matrices
- Matrix factorization techniques (SVD, ALS)

### Mood Classification

Songs are classified into mood categories using:
- K-means clustering on audio features
- Supervised classification with labeled data
- Weighted combination of valence and energy

### Path Generation

Smooth mood transitions are created using:
- Graph-based pathfinding algorithms (Dijkstra, A*)
- Mood distance metrics
- Feature interpolation
- Coherence scoring

## 📈 Performance Metrics

The system is evaluated on:
- **Transition smoothness**: Average mood distance between consecutive songs
- **Target accuracy**: How close the final song is to the target mood
- **User satisfaction**: Subjective ratings from user studies
- **Recommendation diversity**: Variety of artists and genres

## 🛣️ Roadmap

- [x] Data collection from Spotify API
- [x] Audio feature extraction and analysis
- [ ] Collaborative filtering implementation
- [ ] Mood classification model
- [ ] Path generation algorithm
- [ ] Web interface for user interaction
- [ ] User authentication and profile management
- [ ] Playlist export to Spotify
- [ ] Real-time mood detection from listening history
- [ ] Mobile application

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide for Python code
- Add unit tests for new features
- Update documentation for API changes
- Use meaningful commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Spotify** for providing the comprehensive audio features API
- **Russell's Circumplex Model** for the theoretical foundation of mood representation
- The music information retrieval (MIR) community for research and inspiration

## 📧 Contact

Project Link: [https://github.com/yourusername/moodshift](https://github.com/yourusername/moodshift)

## 📚 References

- Russell, J. A. (1980). A circumplex model of affect. Journal of Personality and Social Psychology.
- Spotify Web API Documentation: https://developer.spotify.com/documentation/web-api
- Music Emotion Recognition: A Review: [IEEE Paper](https://ieeexplore.ieee.org)

---

Made with ❤️ for music lovers who want to shift their mood
