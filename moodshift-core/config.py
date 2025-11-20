"""
MoodShift Configuration
Settings and parameters for the recommendation system
"""

# Mood Classification Settings
MOOD_SETTINGS = {
    'valence_threshold': 0.5,
    'energy_threshold': 0.5,
    
    # Mood category definitions
    'mood_categories': {
        'happy_energetic': {
            'valence_range': (0.6, 1.0),
            'energy_range': (0.6, 1.0),
            'description': 'Upbeat, exciting, joyful',
            'keywords': ['party', 'dance', 'upbeat', 'energetic']
        },
        'happy_calm': {
            'valence_range': (0.6, 1.0),
            'energy_range': (0.0, 0.4),
            'description': 'Peaceful, content, serene',
            'keywords': ['chill', 'relaxing', 'peaceful', 'acoustic']
        },
        'sad_calm': {
            'valence_range': (0.0, 0.4),
            'energy_range': (0.0, 0.4),
            'description': 'Melancholic, gentle, reflective',
            'keywords': ['sad', 'melancholy', 'emotional', 'slow']
        },
        'sad_energetic': {
            'valence_range': (0.0, 0.4),
            'energy_range': (0.6, 1.0),
            'description': 'Intense, angry, aggressive',
            'keywords': ['intense', 'aggressive', 'dark', 'heavy']
        },
        'neutral': {
            'valence_range': (0.4, 0.6),
            'energy_range': (0.4, 0.6),
            'description': 'Balanced, moderate',
            'keywords': ['moderate', 'balanced', 'middle']
        }
    }
}

# Path Generation Settings
PATH_SETTINGS = {
    'max_mood_jump': 0.25,  # Maximum distance between consecutive songs
    'smoothness_weight': 0.7,  # Weight for smoothness vs. direct path
    'min_playlist_length': 5,
    'max_playlist_length': 50,
    'default_playlist_length': 10
}

# Collaborative Filtering Settings
CF_SETTINGS = {
    'similarity_metric': 'cosine',
    'n_recommendations': 10,
    'diversity_weight': 0.3,
    
    # Audio features to use for similarity
    'feature_weights': {
        'valence': 1.5,
        'energy': 1.5,
        'danceability': 1.0,
        'acousticness': 0.8,
        'instrumentalness': 0.6,
        'speechiness': 0.5,
        'tempo': 0.7,
        'loudness': 0.5
    }
}

# Data Paths
DATA_PATHS = {
    'raw_data': '../data/raw/',
    'processed_data': '../data/processed/',
    'models': '../data/models/',
    'playlists': '../data/playlists/'
}

# Model Settings
MODEL_SETTINGS = {
    'random_seed': 42,
    'test_size': 0.2,
    'validation_size': 0.1
}

# Feature Engineering
FEATURE_SETTINGS = {
    # Normalize these features to 0-1 range
    'normalize': ['tempo', 'loudness', 'duration_ms'],
    
    # Use these features for recommendations
    'recommendation_features': [
        'valence', 'energy', 'danceability', 'acousticness',
        'instrumentalness', 'speechiness', 'tempo', 'loudness'
    ],
    
    # Use these features for mood classification
    'mood_features': ['valence', 'energy']
}

# Logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}
