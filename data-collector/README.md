# 📊 MoodShift Data Collector

This module handles data collection from the Spotify Web API. It gathers track information and audio features to build a comprehensive music dataset for mood-based recommendations.

## 🎯 Purpose

The data collector serves as the foundation for the MoodShift system by:
- Collecting diverse music tracks across different mood categories
- Extracting audio features that correlate with emotional states
- Building a dataset suitable for collaborative filtering and mood analysis
- Providing tools to analyze and validate the collected data

## 📁 Files

- **`collector.py`**: Main data collection script
- **`analyzer.py`**: Data analysis and visualization utilities
- **`requirements.txt`**: Python dependencies for this module

## 🚀 Quick Start

### 1. Set Up Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Note your **Client ID** and **Client Secret**

### 2. Configure Credentials

Create a `.env` file in the project root:

```bash
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

Or edit `collector.py` directly (line ~220):

```python
CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Collect Data

```bash
python collector.py
```

This will:
- Collect ~500 tracks across 5 mood categories
- Save results to `../data/raw/spotify_mood_dataset.csv`

## 📊 Collection Strategies

### Strategy 1: Mood-Based Collection (Default)

Automatically collects tracks across predefined mood categories:

```python
from collector import SpotifyDataCollector

collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
df = collector.collect_diverse_dataset(num_tracks_per_category=100)
df.to_csv('../data/raw/spotify_mood_dataset.csv', index=False)
```

**Mood Categories:**
- `happy_energetic`: High valence (0.8), High energy (0.8)
- `happy_calm`: High valence (0.8), Low energy (0.3)
- `sad_energetic`: Low valence (0.2), High energy (0.8)
- `sad_calm`: Low valence (0.2), Low energy (0.3)
- `neutral`: Medium valence (0.5), Medium energy (0.5)

### Strategy 2: Playlist-Based Collection

Collect from specific Spotify playlists:

```python
playlist_ids = [
    '37i9dQZF1DX3rxVfibe1L0',  # Mood Booster
    '37i9dQZF1DX3YSRoSdA634',  # Chill Hits
    '37i9dQZF1DWSf2lDTn6N2x',  # Sad Songs
    '37i9dQZF1DX0XUsuxWHRQd',  # RapCaviar
]

df = collector.collect_from_playlists(playlist_ids)
```

**Finding Playlist IDs:**
- Open a playlist in Spotify
- Click Share → Copy link to playlist
- Extract ID from URL: `https://open.spotify.com/playlist/[PLAYLIST_ID]`

### Strategy 3: Custom Mood Parameters

Search for tracks with specific mood characteristics:

```python
mood_params = {
    'target_valence': 0.9,      # Very happy
    'target_energy': 0.7,       # High energy
    'target_danceability': 0.8, # Very danceable
    'target_acousticness': 0.2  # Mostly electronic
}

tracks = collector.search_tracks_by_mood(mood_params, limit=50)
```

## 🔍 Data Analysis

After collecting data, analyze it using the analyzer:

```bash
python analyzer.py
```

This will:
- Generate statistics about the dataset
- Create visualizations (mood space, correlations, tempo distribution)
- Check data quality
- Identify mood extremes

**Generated Files:**
- `mood_space.png`: Scatter plot of valence vs. energy
- `feature_correlations.png`: Heatmap of audio feature correlations
- `tempo_distribution.png`: Tempo distribution across moods
- `spotify_mood_dataset_enhanced.csv`: Dataset with computed mood quadrants

## 📈 Audio Features

Each track includes the following Spotify audio features:

| Feature | Type | Range | Description |
|---------|------|-------|-------------|
| `valence` | float | 0.0-1.0 | Musical positivity (happiness) |
| `energy` | float | 0.0-1.0 | Intensity and activity level |
| `danceability` | float | 0.0-1.0 | Suitability for dancing |
| `tempo` | float | ~40-200 | Beats per minute (BPM) |
| `acousticness` | float | 0.0-1.0 | Acoustic vs. electronic |
| `instrumentalness` | float | 0.0-1.0 | Likelihood of no vocals |
| `speechiness` | float | 0.0-1.0 | Presence of spoken words |
| `loudness` | float | -60-0 | Overall loudness (dB) |
| `liveness` | float | 0.0-1.0 | Presence of audience |
| `key` | int | 0-11 | Musical key (pitch class) |
| `mode` | int | 0-1 | Major (1) or minor (0) |

**Key Features for Mood:**
- **Valence + Energy**: Primary mood indicators (Russell's model)
- **Tempo**: Influences perceived energy
- **Acousticness**: Affects emotional texture
- **Mode**: Major keys often happier than minor

## 💡 Best Practices

### Data Quality

1. **Diversity**: Collect from multiple genres and eras
2. **Balance**: Ensure even distribution across mood categories
3. **Size**: Aim for 1,000-10,000 tracks for good coverage
4. **Deduplication**: Remove duplicate tracks automatically handled

### Rate Limiting

The collector includes built-in rate limiting:
- 0.1s delay between batch requests
- 0.5s delay between playlists/mood categories

To be extra safe:
```python
import time
time.sleep(1)  # Add longer delays if needed
```

### API Quotas

Spotify has generous rate limits, but be mindful:
- **Standard**: 180 requests per minute
- **Extended**: Higher limits for registered apps

## 🐛 Troubleshooting

### "Invalid client" error
- Check your Client ID and Client Secret
- Ensure no extra spaces in credentials
- Verify app is created in Spotify Dashboard

### Empty or incomplete results
- Some tracks may not have audio features
- The collector filters these out automatically
- Try different playlists or mood parameters

### Rate limiting errors
- Increase `time.sleep()` delays
- Reduce `num_tracks_per_category`
- Collect data in smaller batches

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.8+)

## 📊 Expected Output

A successful collection will produce:

```
Collecting tracks for different mood categories...
  Collecting happy_energetic tracks...
  Collecting happy_calm tracks...
  Collecting sad_energetic tracks...
  Collecting sad_calm tracks...
  Collecting neutral tracks...

Collected 487 unique tracks
Fetching audio features...

Dataset shape: (487, 18)
Dataset saved to '../data/raw/spotify_mood_dataset.csv'
```

## 🔄 Updating the Dataset

To expand your dataset:

```python
# Load existing data
existing_df = pd.read_csv('../data/raw/spotify_mood_dataset.csv')

# Collect new data
collector = SpotifyDataCollector(CLIENT_ID, CLIENT_SECRET)
new_df = collector.collect_diverse_dataset(num_tracks_per_category=200)

# Combine and deduplicate
combined_df = pd.concat([existing_df, new_df])
combined_df = combined_df.drop_duplicates(subset=['track_id'])

# Save
combined_df.to_csv('../data/raw/spotify_mood_dataset.csv', index=False)
```

## 📚 API Reference

### `SpotifyDataCollector`

Main class for collecting Spotify data.

**Methods:**

- `get_playlist_tracks(playlist_id)`: Get all tracks from a playlist
- `get_audio_features(track_ids)`: Get audio features for tracks
- `search_tracks_by_mood(mood_params, limit)`: Search tracks by mood
- `collect_diverse_dataset(num_tracks_per_category)`: Collect diverse dataset
- `collect_from_playlists(playlist_ids)`: Collect from playlists

### `DatasetAnalyzer`

Class for analyzing collected data.

**Methods:**

- `basic_statistics()`: Display dataset statistics
- `mood_distribution()`: Analyze mood distribution
- `visualize_mood_space(save_path)`: Create mood space plot
- `feature_correlations(save_path)`: Create correlation heatmap
- `find_mood_extremes()`: Find extreme mood tracks
- `data_quality_check()`: Check data quality

## 🎓 Further Reading

- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Spotipy Library Docs](https://spotipy.readthedocs.io/)
- [Audio Features Explanation](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)
- [Russell's Circumplex Model](https://en.wikipedia.org/wiki/Emotion_classification#Circumplex_model)

---

[← Back to Main README](../README.md)