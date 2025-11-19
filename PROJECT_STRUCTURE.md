# MoodShift - Project Structure Setup Guide

This guide will help you set up the complete MoodShift repository structure.

## 📁 Recommended Repository Structure

```
moodshift/
│
├── .github/                          # GitHub specific files
│   ├── workflows/
│   │   └── tests.yml                # CI/CD workflow
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── data-collector/                   # Data collection module
│   ├── __init__.py
│   ├── collector.py                 # Spotify data collector
│   ├── analyzer.py                  # Data analysis tools
│   ├── requirements.txt             # Module-specific dependencies
│   └── README.md                    # Module documentation
│
├── moodshift-core/                   # Main recommendation system
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── collaborative_filtering.py
│   │   ├── mood_classifier.py
│   │   └── path_generator.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── preprocessing.py
│   │   └── feature_extraction.py
│   ├── config.py
│   ├── main.py                      # CLI interface
│   └── README.md
│
├── data/                             # Data directory (not tracked)
│   ├── raw/                         # Raw collected data
│   │   └── .gitkeep
│   ├── processed/                   # Processed datasets
│   │   └── .gitkeep
│   └── models/                      # Saved model files
│       └── .gitkeep
│
├── notebooks/                        # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_mood_analysis.ipynb
│   ├── 03_collaborative_filtering.ipynb
│   └── 04_path_generation.ipynb
│
├── tests/                           # Unit tests
│   ├── __init__.py
│   ├── test_collector.py
│   ├── test_mood_classifier.py
│   ├── test_collaborative_filtering.py
│   └── test_path_generator.py
│
├── docs/                            # Additional documentation
│   ├── api.md
│   ├── architecture.md
│   └── user_guide.md
│
├── .env.example                     # Example environment variables
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT License
├── README.md                        # Main project README
├── CONTRIBUTING.md                  # Contribution guidelines
├── requirements.txt                 # Main dependencies
└── setup.py                         # Package setup (optional)
```

## 🚀 Setup Steps

### 1. Initialize Repository

```bash
# Create main directory
mkdir moodshift
cd moodshift

# Initialize git
git init
```

### 2. Create Directory Structure

```bash
# Create main directories
mkdir -p data-collector
mkdir -p moodshift-core/models
mkdir -p moodshift-core/utils
mkdir -p data/{raw,processed,models}
mkdir -p notebooks
mkdir -p tests
mkdir -p docs
mkdir -p .github/workflows
mkdir -p .github/ISSUE_TEMPLATE

# Create .gitkeep files for empty directories
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/models/.gitkeep
```

### 3. Add Configuration Files

Copy the files you've downloaded to the appropriate locations:

```bash
# Main repository files
# - README.md → moodshift/README.md
# - .gitignore → moodshift/.gitignore
# - LICENSE → moodshift/LICENSE
# - requirements.txt → moodshift/requirements.txt
# - CONTRIBUTING.md → moodshift/CONTRIBUTING.md

# Data collector files
# - spotify_data_collector.py → data-collector/collector.py
# - analyze_dataset.py → data-collector/analyzer.py
# - data-collector-README.md → data-collector/README.md

# Core module
# - moodshift-core-README.md → moodshift-core/README.md
```

### 4. Create __init__.py Files

```bash
# Create package init files
touch data-collector/__init__.py
touch moodshift-core/__init__.py
touch moodshift-core/models/__init__.py
touch moodshift-core/utils/__init__.py
touch tests/__init__.py
```

### 5. Create .env.example

```bash
cat > .env.example << 'EOF'
# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here

# Data Paths
RAW_DATA_PATH=data/raw
PROCESSED_DATA_PATH=data/processed
MODEL_PATH=data/models

# Model Configuration
N_FACTORS=50
N_NEIGHBORS=20
VALENCE_THRESHOLD=0.5
ENERGY_THRESHOLD=0.5
EOF
```

### 6. Initial Commit

```bash
# Stage all files
git add .

# Initial commit
git commit -m "Initial commit: Project structure and data collector"
```

### 7. Create GitHub Repository

1. Go to GitHub and create a new repository named "moodshift"
2. Don't initialize with README (you already have one)
3. Connect your local repository:

```bash
git remote add origin https://github.com/yourusername/moodshift.git
git branch -M main
git push -u origin main
```

## 📝 File Organization Tips

### data-collector/
- Keep all data collection code here
- Should be runnable independently
- Output goes to `../data/raw/`

### moodshift-core/
- Core recommendation logic
- Import data from `../data/`
- Models can be imported elsewhere

### data/
- **raw/**: Unprocessed data from Spotify
- **processed/**: Cleaned and prepared datasets
- **models/**: Saved trained models (.pkl, .h5, etc.)
- All subdirectories in .gitignore (don't commit large data)

### notebooks/
- Exploratory data analysis
- Prototyping new features
- Visualization and reporting
- Name with numbers for ordering

### tests/
- Mirror structure of main code
- One test file per module
- Use pytest conventions

## 🔧 Development Workflow

### Working on Data Collection

```bash
cd data-collector
python collector.py
python analyzer.py
```

### Working on Core System

```bash
cd moodshift-core
python main.py --current-mood sad --target-mood happy
```

### Running Tests

```bash
# From project root
pytest tests/

# With coverage
pytest --cov=. tests/
```

### Using Notebooks

```bash
jupyter notebook notebooks/
```

## 📦 Creating a Release

### 1. Update Version

Update version in relevant files:
- `setup.py`
- `moodshift-core/__init__.py`
- `data-collector/__init__.py`

### 2. Update CHANGELOG

Create/update CHANGELOG.md with new features, fixes, and breaking changes.

### 3. Tag Release

```bash
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0
```

### 4. Create GitHub Release

- Go to Releases on GitHub
- Click "Create a new release"
- Select your tag
- Add release notes
- Attach any binaries if needed

## 🎯 Next Steps

1. **Set up CI/CD**: Add GitHub Actions for automated testing
2. **Add documentation**: Create detailed API docs
3. **Implement core features**: Build collaborative filtering and path generation
4. **Add examples**: Create example scripts in `examples/` directory
5. **Create demo**: Build a simple web interface or CLI demo

## 📚 Additional Files to Consider

### setup.py (for pip installation)

```python
from setuptools import setup, find_packages

setup(
    name="moodshift",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "spotipy>=2.23.0",
        "pandas>=2.1.0",
        "numpy>=1.24.3",
        "scikit-learn>=1.3.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Mood-based music recommendation system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/moodshift",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
```

### .github/workflows/tests.yml (CI/CD)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    - name: Run tests
      run: pytest --cov=. tests/
```

## ✅ Checklist

Before making repository public:

- [ ] All sensitive data removed (API keys, credentials)
- [ ] .gitignore properly configured
- [ ] README.md is complete and clear
- [ ] LICENSE file added
- [ ] CONTRIBUTING.md guidelines clear
- [ ] Tests passing
- [ ] Code formatted and linted
- [ ] Example usage documented
- [ ] .env.example provided

---

Happy coding! 🎵
