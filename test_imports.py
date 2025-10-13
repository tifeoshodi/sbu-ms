#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
Run this before deploying to Streamlit Cloud
"""

print("Testing imports for SBU/PO Dashboard...")

try:
    import streamlit as st
    print("✓ streamlit imported successfully")
except ImportError as e:
    print(f"✗ streamlit import failed: {e}")

try:
    import pandas as pd
    print("✓ pandas imported successfully")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    print("✓ plotly imported successfully")
except ImportError as e:
    print(f"✗ plotly import failed: {e}")

try:
    import sqlite3
    print("✓ sqlite3 imported successfully")
except ImportError as e:
    print(f"✗ sqlite3 import failed: {e}")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except ImportError as e:
    print(f"✗ numpy import failed: {e}")

try:
    from database.db_manager import DatabaseManager
    print("✓ database.db_manager imported successfully")
except ImportError as e:
    print(f"✗ database.db_manager import failed: {e}")

try:
    import openpyxl
    print("✓ openpyxl imported successfully")
except ImportError as e:
    print(f"✗ openpyxl import failed: {e}")

print("\nImport testing complete!")
print("If all imports show ✓, the app should deploy successfully to Streamlit Cloud.")
