# News Digest Project Guide

## Commands
- **Run**: `python main.py` (or `./run.sh`)
- **Install**: `pip install -r requirements.txt`
- **Deploy**: `./deploy_vps.sh`
- **Environment**: Ensure `venv` is activated (`source venv/bin/activate`)

## Architecture
- **Entry Points**:
  - `main.py`: Main application entry
  - `morning_main.py`: Morning specific execution
- **Modules**:
  - `news_fetcher.py`: Fetches news data
  - `summarizer.py`: Summarizes content using AI
  - `email_sender.py`: Handles email delivery
  - `config.py`: Configuration settings
- **Logs**: `news_digest.log`, `news_digest.err.log`

## Code Style
- **Python**: Follow PEP 8 guidelines.
- **Imports**: Absolute imports preferred.
- **Config**: Use `config.py` for variables, do not hardcode credentials.

## Critical Context
- This project runs on a VPS (deployment script included).
- Uses `venv` for dependency management.
