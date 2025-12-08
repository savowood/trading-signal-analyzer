# Installation Guide - Trading Signal Analyzer v2.0

This guide covers installation for the modular version (v2.0+).

For v1.0 (monolithic), see main README.md.

---

## Requirements

### System Requirements
- **Python:** 3.8 or higher
- **Operating System:** Windows, macOS, or Linux
- **Internet:** Required for real-time market data
- **Disk Space:** ~50MB for package + dependencies

### Python Version Check
```bash
python --version
# Should show 3.8.0 or higher
```

---

## Installation Methods

### Method 1: Development Installation (Recommended for Testing)

Install in editable mode to make changes and see them immediately:

```bash
# Clone the repository
git clone -b v2.0-dev https://github.com/savowood/trading-signal-analyzer.git
cd trading-signal-analyzer

# Install in development mode
pip install -e .

# Or with all optional dependencies
pip install -e ".[all]"
```

**Advantages:**
- Changes to code take effect immediately
- Easy to customize and test
- Can pull updates with `git pull`

**Usage:**
```bash
# Run from anywhere
python -m trading_analyzer

# Or use the CLI command
trading-analyzer
```

### Method 2: Standard Installation (Coming Soon)

Once released to PyPI:

```bash
# Install from PyPI (when available)
pip install trading-signal-analyzer

# With optional dependencies
pip install trading-signal-analyzer[all]
```

### Method 3: From Source (Stable Releases)

Install from a specific release:

```bash
# Download and extract release
wget https://github.com/savowood/trading-signal-analyzer/archive/v2.0.0.tar.gz
tar -xzf v2.0.0.tar.gz
cd trading-signal-analyzer-2.0.0

# Install
pip install .
```

---

## Optional Dependencies

### Polygon/Massive API (Professional Market Data)
```bash
pip install trading-signal-analyzer[polygon]
```

### News Integration
```bash
pip install trading-signal-analyzer[news]
```

### Social Sentiment (Reddit)
```bash
pip install trading-signal-analyzer[social]
```

### Development Tools
```bash
pip install trading-signal-analyzer[dev]
```

### Everything
```bash
pip install trading-signal-analyzer[all]
```

---

## Virtual Environment (Recommended)

Use a virtual environment to avoid conflicts:

### Using venv (Built-in)
```bash
# Create virtual environment
python -m venv trading-env

# Activate (Linux/macOS)
source trading-env/bin/activate

# Activate (Windows)
trading-env\Scripts\activate

# Install package
pip install -e .

# Deactivate when done
deactivate
```

### Using conda
```bash
# Create environment
conda create -n trading python=3.10

# Activate
conda activate trading

# Install package
pip install -e .

# Deactivate
conda deactivate
```

---

## Verification

### Test Installation
```bash
# Should show version and help
trading-analyzer --help

# Or
python -m trading_analyzer --help
```

### Import Test
```python
python -c "
from trading_analyzer import VERSION
from trading_analyzer.main import main
print(f'Trading Signal Analyzer v{VERSION} installed successfully!')
"
```

### Run Quick Test
```bash
# Launch the application
python -m trading_analyzer

# Accept disclaimer
# Select any scanner
# Run a quick test scan
```

---

## Configuration

### Settings File
Create `~/.trading_analyzer` for custom settings:

```json
{
  "disclaimer_acknowledged": true,
  "pressure_cooker_disclaimer_acknowledged": true,
  "api_keys": {
    "polygon": "YOUR_API_KEY_HERE",
    "newsapi": null,
    "reddit_client_id": null,
    "reddit_client_secret": null
  },
  "cache_settings": {
    "scan_results": 900,
    "stock_data": 3600,
    "options_data": 1800
  },
  "database": {
    "path": "~/Documents/trading_analyzer.db",
    "auto_save": true,
    "max_history_days": 90
  }
}
```

### Database Location
Default: `~/Documents/trading_analyzer.db`

To change:
```bash
export TRADING_ANALYZER_DB="/path/to/custom/location.db"
```

---

## Upgrading

### Development Installation
```bash
cd /path/to/trading-signal-analyzer
git pull
pip install -e . --upgrade
```

### PyPI Installation (When Available)
```bash
pip install trading-signal-analyzer --upgrade
```

---

## Uninstallation

### Remove Package
```bash
pip uninstall trading-signal-analyzer
```

### Remove Settings (Optional)
```bash
rm ~/.trading_analyzer
```

### Remove Database (Optional)
```bash
rm ~/Documents/trading_analyzer.db
```

---

## Troubleshooting

### "Module not found" Error
```bash
# Verify installation
pip list | grep trading-signal-analyzer

# If not found, reinstall
pip install -e .
```

### Permission Errors (Linux/macOS)
```bash
# Install without sudo (use virtual environment instead)
# Or install for user only
pip install --user -e .
```

### Windows PATH Issues
```bash
# Add Python Scripts to PATH
# Or run with full path:
python -m trading_analyzer
```

### ImportError: No module named 'trading_analyzer'
```bash
# Make sure you're in the right directory
cd /path/to/trading-signal-analyzer

# Check PYTHONPATH
echo $PYTHONPATH

# Reinstall
pip install -e .
```

### Database Permission Error
```bash
# Check database location exists
ls -la ~/Documents/trading_analyzer.db

# Fix permissions
chmod 644 ~/Documents/trading_analyzer.db
```

---

## Platform-Specific Notes

### macOS
- Use Python 3.8+ from python.org or Homebrew
- Avoid system Python (/usr/bin/python)

```bash
# Install via Homebrew
brew install python@3.11

# Install package
pip3.11 install -e .
```

### Windows
- Install Python from python.org
- Make sure "Add Python to PATH" is checked during installation

```cmd
# Install package
pip install -e .

# Run
python -m trading_analyzer
```

### Linux
- Use system Python or pyenv

```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip

# Fedora
sudo dnf install python3 python3-pip

# Install package
pip3 install --user -e .
```

---

## Docker Installation (Advanced)

Coming soon: Pre-built Docker image for containerized deployment.

```bash
# Pull image (when available)
docker pull ghcr.io/savowood/trading-signal-analyzer:v2.0

# Run
docker run -it --rm \
  -v ~/.trading_analyzer:/root/.trading_analyzer \
  trading-signal-analyzer:v2.0
```

---

## Development Setup

For contributors:

```bash
# Clone and setup
git clone https://github.com/savowood/trading-signal-analyzer.git
cd trading-signal-analyzer
git checkout v2.0-dev

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install

# Run tests
pytest

# Format code
black trading_analyzer/

# Lint
flake8 trading_analyzer/
```

---

## Getting Help

### Documentation
- **README.md** - Feature overview
- **CHANGELOG.md** - Version history
- **MIGRATION_GUIDE_v1_to_v2.md** - Upgrade from v1.0
- **POLYGON_SETUP_GUIDE.md** - API setup

### Support
- **Issues:** https://github.com/savowood/trading-signal-analyzer/issues
- **Discussions:** https://github.com/savowood/trading-signal-analyzer/discussions

---

## Next Steps

After installation:

1. ✅ Run first scan to test
2. ✅ Configure settings file
3. ✅ Add Polygon API key (optional)
4. ✅ Explore features
5. ✅ Read migration guide (if coming from v1.0)

**Happy trading!** 📈
