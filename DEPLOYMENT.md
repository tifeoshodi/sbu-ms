# Streamlit Cloud Deployment Guide

## Files for Deployment

✅ **Required Files:**
- `sbu_app.py` - Main application file
- `requirements.txt` - Python dependencies
- `database/db_manager.py` - Database manager
- `database/__init__.py` - Package init
- `.streamlit/config.toml` - Streamlit configuration
- `packages.txt` - System dependencies (if needed)

## Deployment Steps

1. **Push to GitHub:**
   - Ensure all files are committed and pushed
   - Main branch should contain all required files

2. **Deploy to Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Connect your GitHub repository
   - Set main file: `sbu_app.py`
   - Deploy

3. **Troubleshooting:**
   - If imports fail, check requirements.txt
   - If app doesn't start, check logs in Streamlit Cloud
   - Ensure all files are in the repository

## Common Issues & Solutions

### ModuleNotFoundError: plotly
- **Solution:** Ensure `plotly>=5.17.0` is in requirements.txt
- **Check:** Run `python test_imports.py` locally first

### Database not found
- **Solution:** The app will create the database automatically
- **Note:** Database file is created in the deployed environment

### Theme not working
- **Solution:** Check `.streamlit/config.toml` is properly formatted

## File Structure for Deployment
```
SBUs/
├── .streamlit/
│   └── config.toml
├── database/
│   ├── __init__.py
│   └── db_manager.py
├── sbu_app.py          # Main file for Streamlit Cloud
├── requirements.txt     # Dependencies
├── packages.txt         # System packages (optional)
└── test_imports.py     # Local testing
```

## Testing Before Deployment
```bash
# Test imports
python test_imports.py

# Test app locally
streamlit run sbu_app.py
```
