# 🚀 MoodShift - Quick Start Checklist

Use this checklist to set up your MoodShift GitHub repository step by step.

## ✅ Phase 1: Repository Setup

### Create Repository
- [ ] Create new repository on GitHub named "moodshift"
- [ ] Choose "Public" or "Private"
- [ ] Do NOT initialize with README, .gitignore, or license
- [ ] Clone the empty repository to your local machine

### Add Core Files
- [ ] Copy `README.md` to repository root
- [ ] Copy `.gitignore` to repository root
- [ ] Copy `LICENSE` to repository root
- [ ] Copy `requirements.txt` to repository root
- [ ] Copy `CONTRIBUTING.md` to repository root

### Create Directory Structure
```bash
mkdir -p data-collector
mkdir -p moodshift-core/models
mkdir -p moodshift-core/utils
mkdir -p data/{raw,processed,models}
mkdir -p notebooks
mkdir -p tests
mkdir -p docs
```

### Add .gitkeep Files
```bash
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/models/.gitkeep
```

## ✅ Phase 2: Data Collector Module

### Set Up Data Collector
- [ ] Create `data-collector/` directory
- [ ] Copy `spotify_data_collector.py` → `data-collector/collector.py`
- [ ] Copy `analyze_dataset.py` → `data-collector/analyzer.py`
- [ ] Copy `data-collector-README.md` → `data-collector/README.md`
- [ ] Create `data-collector/__init__.py` (can be empty)
- [ ] Create `data-collector/requirements.txt`:
```
spotipy==2.23.0
pandas==2.1.0
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
```

### Get Spotify Credentials
- [ ] Go to https://developer.spotify.com/dashboard
- [ ] Create a new app
- [ ] Copy Client ID and Client Secret
- [ ] Create `.env` file in repository root:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```
- [ ] Add `.env` to `.gitignore` (should already be there)

### Test Data Collector
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Update credentials in `collector.py` or use `.env`
- [ ] Run: `cd data-collector && python collector.py`
- [ ] Verify data saved to `../data/raw/spotify_mood_dataset.csv`
- [ ] Run: `python analyzer.py`
- [ ] Check generated visualizations

## ✅ Phase 3: Core Module Setup (Placeholder)

### Create Core Structure
- [ ] Create `moodshift-core/` directory
- [ ] Create `moodshift-core/__init__.py`
- [ ] Create `moodshift-core/models/` directory
- [ ] Create `moodshift-core/models/__init__.py`
- [ ] Create `moodshift-core/utils/` directory
- [ ] Create `moodshift-core/utils/__init__.py`
- [ ] Copy `moodshift-core-README.md` → `moodshift-core/README.md`

### Create Placeholder Files
Create these empty files for now (to be implemented later):

- [ ] `moodshift-core/models/collaborative_filtering.py`
- [ ] `moodshift-core/models/mood_classifier.py`
- [ ] `moodshift-core/models/path_generator.py`
- [ ] `moodshift-core/utils/preprocessing.py`
- [ ] `moodshift-core/utils/feature_extraction.py`
- [ ] `moodshift-core/config.py`
- [ ] `moodshift-core/main.py`

## ✅ Phase 4: Testing Setup

### Create Test Structure
- [ ] Create `tests/` directory
- [ ] Create `tests/__init__.py`
- [ ] Create `tests/test_collector.py` (basic test)
- [ ] Install pytest: `pip install pytest pytest-cov`
- [ ] Run tests: `pytest tests/`

### Example Basic Test
Create `tests/test_collector.py`:
```python
def test_import():
    """Test that collector module can be imported."""
    try:
        import sys
        sys.path.insert(0, 'data-collector')
        from collector import SpotifyDataCollector
        assert True
    except ImportError:
        assert False, "Could not import SpotifyDataCollector"
```

## ✅ Phase 5: Documentation

### Add Documentation Files
- [ ] Create `docs/` directory
- [ ] Create `.env.example`:
```
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### Create Initial Notebooks (Optional)
- [ ] Create `notebooks/01_data_exploration.ipynb`
- [ ] Add basic data exploration code

## ✅ Phase 6: Git & GitHub

### Initial Commit
```bash
git add .
git commit -m "Initial commit: Project structure and data collector

- Add main README with project overview
- Add data collector module with Spotify API integration
- Add data analysis tools
- Add project documentation and guidelines
- Set up directory structure for future development"
```

### Push to GitHub
```bash
git branch -M main
git remote add origin https://github.com/yourusername/moodshift.git
git push -u origin main
```

### Configure Repository Settings
- [ ] Add repository description
- [ ] Add topics/tags: `music`, `recommendation-system`, `spotify`, `machine-learning`, `python`
- [ ] Add website (if you have one)
- [ ] Enable Issues
- [ ] Enable Discussions (optional)

### Add GitHub-Specific Files (Optional but Recommended)
- [ ] Create `.github/ISSUE_TEMPLATE/bug_report.md`
- [ ] Create `.github/ISSUE_TEMPLATE/feature_request.md`
- [ ] Create `.github/workflows/tests.yml` for CI/CD

## ✅ Phase 7: First Release

### Prepare for Release
- [ ] Ensure all tests pass
- [ ] Update README if needed
- [ ] Create CHANGELOG.md
- [ ] Tag version: `git tag -a v0.1.0 -m "Initial release - Data collector"`
- [ ] Push tag: `git push origin v0.1.0`

### Create GitHub Release
- [ ] Go to Releases → Create new release
- [ ] Select tag v0.1.0
- [ ] Write release notes
- [ ] Publish release

## ✅ Phase 8: Next Steps

### Immediate Tasks
- [ ] Collect initial dataset (1000+ tracks)
- [ ] Analyze data distribution
- [ ] Document findings in notebook

### Future Development
- [ ] Implement collaborative filtering model
- [ ] Implement mood classifier
- [ ] Implement path generation algorithm
- [ ] Create CLI interface
- [ ] Add web interface (optional)
- [ ] Deploy as web service (optional)

## 📝 Quick Commands Reference

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Collect data
cd data-collector
python collector.py

# Analyze data
python analyzer.py

# Run tests
pytest tests/

# Format code
black .

# Check style
flake8 --max-line-length=100
```

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push branch
git push origin feature/your-feature

# After PR is merged
git checkout main
git pull origin main
git branch -d feature/your-feature
```

## 🎯 Success Criteria

Your repository is ready when:
- [ ] All files are properly organized
- [ ] README is clear and informative
- [ ] Data collector works and produces data
- [ ] Tests run successfully
- [ ] Repository is pushed to GitHub
- [ ] Documentation is complete
- [ ] .gitignore prevents sensitive data commits
- [ ] You can clone and run the project on a fresh machine

## 🆘 Troubleshooting

### "Module not found" errors
- Check that `__init__.py` files exist in all packages
- Verify Python path includes the project directory
- Try: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

### Spotify API errors
- Verify credentials are correct
- Check that .env file is in the right location
- Ensure app is created in Spotify Dashboard

### Git push rejected
- Pull latest changes first: `git pull origin main`
- Resolve any merge conflicts
- Push again: `git push origin main`

## 📚 Resources

- [GitHub Docs](https://docs.github.com/)
- [Spotify API Docs](https://developer.spotify.com/documentation/web-api)
- [Python Packaging Guide](https://packaging.python.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

🎉 Congratulations! You're ready to build MoodShift!
