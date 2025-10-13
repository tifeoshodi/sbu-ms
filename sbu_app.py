"""
SBU/PO Dashboard - Streamlit Application
Strategic Business Unit and Purchase Order Management System
Migrated from PySide6 to Streamlit for better usability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
from datetime import datetime, date, timedelta
import locale
from typing import Dict, List, Optional
import numpy as np

# Import our database manager
from database.db_manager import DatabaseManager

# Configure pandas to suppress FutureWarnings
pd.set_option('future.no_silent_downcasting', True)


def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="PO Dashboard - Oil & Gas Engineering",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Theme toggle - default to dark mode
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True
    
    # Professional CSS with dark/light theme support
    theme_colors = {
        'light': {
            'primary': '#1e8449',
            'secondary': '#27ae60',
            'accent': '#d5f4e6',
            'background': '#ffffff',
            'surface': '#f8f9fa',
            'text_primary': '#2c3e50',
            'text_secondary': '#5d6d7e',
            'border': '#d5dbdb',
            'shadow': 'rgba(0,0,0,0.1)'
        },
        'dark': {
            'primary': '#27ae60',
            'secondary': '#2ecc71',
            'accent': '#1a4a34',
            'background': '#0e1117',
            'surface': '#262730',
            'text_primary': '#fafafa',
            'text_secondary': '#a0a0a0',
            'border': '#4a4a4a',
            'shadow': 'rgba(255,255,255,0.1)'
        }
    }
    
    current_theme = 'dark' if st.session_state.dark_mode else 'light'
    colors = theme_colors[current_theme]
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Root variables for theme */
    :root {{
        --primary-color: {colors['primary']};
        --secondary-color: {colors['secondary']};
        --accent-color: {colors['accent']};
        --background-color: {colors['background']};
        --surface-color: {colors['surface']};
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --border-color: {colors['border']};
        --shadow-color: {colors['shadow']};
    }}
    
    /* Global font and base styling */
    .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: var(--background-color);
        color: var(--text-primary);
    }}
    
    /* Typography hierarchy */
    h1, .main-title {{
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.25rem;
        color: var(--primary-color);
        margin-bottom: 1.5rem;
        letter-spacing: -0.025em;
    }}
    
    h2, .section-title {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.75rem;
        color: var(--text-primary);
        margin-bottom: 1rem;
        letter-spacing: -0.015em;
    }}
    
    h3, .subsection-title {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.25rem;
        color: var(--text-primary);
        margin-bottom: 0.75rem;
    }}
    
    /* Professional header */
    .main-header {{
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        padding: 2.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 12px var(--shadow-color);
    }}
    
    .main-header h1 {{
        color: white !important;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }}
    
    .main-header p {{
        color: rgba(255,255,255,0.9) !important;
        margin: 0.75rem 0 0 0;
        font-size: 1.125rem;
        font-weight: 500;
    }}
    
    /* Professional metric cards */
    .metric-card {{
        background: var(--surface-color);
        padding: 1rem 0.75rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px var(--shadow-color);
        text-align: center;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 130px;
        max-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }}
    
    .metric-card:hover {{
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px var(--shadow-color);
    }}
    
    .metric-value {{
        font-family: 'Inter', sans-serif;
        font-size: clamp(1.2rem, 1.5vw, 1.8rem);
        font-weight: 700;
        color: var(--primary-color);
        margin: 0.3rem 0;
        line-height: 1.2;
        word-break: break-word;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    .metric-label {{
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.7rem, 0.8vw, 0.875rem);
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    .metric-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: clamp(0.65rem, 0.75vw, 0.8rem);
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 0.25rem;
        opacity: 0.8;
        line-height: 1.3;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    
    /* Professional form styling */
    .stSelectbox label, .stTextInput label, .stDateInput label, .stNumberInput label {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.875rem !important;
        color: var(--text-primary) !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .stSelectbox > div > div, .stTextInput > div > div > input, .stDateInput > div > div > input {{
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        font-family: 'Inter', sans-serif !important;
    }}
    
    /* Professional buttons */
    .stButton > button {{
        font-family: 'Inter', sans-serif;
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        text-transform: none;
        letter-spacing: 0.025em;
    }}
    
    .stButton > button:hover {{
        background-color: var(--secondary-color);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px var(--shadow-color);
    }}
    
    /* Navigation buttons styling */
    div[data-testid="stSidebar"] .stButton > button {{
        width: 100%;
        margin-bottom: 0.5rem;
        font-size: 0.825rem;
        padding: 0.6rem 1rem;
        font-weight: 500;
    }}
    
    /* Primary navigation button */
    div[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background-color: var(--primary-color);
        color: white;
        font-weight: 600;
        box-shadow: 0 2px 6px var(--shadow-color);
    }}
    
    /* Secondary navigation button */
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
        background-color: var(--surface-color);
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        font-weight: 500;
    }}
    
    div[data-testid="stSidebar"] .stButton > button[kind="secondary"]:hover {{
        background-color: var(--accent-color);
        border-color: var(--primary-color);
        color: var(--primary-color);
        transform: translateY(-1px);
    }}
    
    /* Professional tables */
    .stDataFrame {{
        font-family: 'Inter', sans-serif;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px var(--shadow-color);
        background-color: var(--surface-color);
    }}
    
    /* Data table styling for dark/light mode */
    .stDataFrame table {{
        background-color: var(--surface-color) !important;
        color: var(--text-primary) !important;
    }}
    
    .stDataFrame thead th {{
        background-color: var(--primary-color) !important;
        color: white !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        border: none !important;
    }}
    
    .stDataFrame tbody td {{
        background-color: var(--surface-color) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
        padding: 10px 16px !important;
        border-bottom: 1px solid var(--border-color) !important;
        border-left: none !important;
        border-right: none !important;
    }}
    
    .stDataFrame tbody tr:hover td {{
        background-color: var(--accent-color) !important;
        transition: background-color 0.2s ease !important;
    }}
    
    /* Alternative row styling for better readability */
    .stDataFrame tbody tr:nth-child(even) td {{
        background-color: var(--background-color) !important;
    }}
    
    .stDataFrame tbody tr:nth-child(even):hover td {{
        background-color: var(--accent-color) !important;
    }}
    
    /* Sidebar styling */
    .css-1d391kg {{
        background-color: var(--surface-color) !important;
    }}
    
    .css-12oz5g7 {{
        background-color: var(--surface-color) !important;
    }}
    
    .css-17eq0hr {{
        background-color: var(--surface-color) !important;
    }}
    
    /* Streamlit sidebar container */
    section[data-testid="stSidebar"] {{
        background-color: var(--surface-color) !important;
        overflow-y: hidden !important;
    }}
    
    section[data-testid="stSidebar"] > div {{
        background-color: var(--surface-color) !important;
        overflow-y: hidden !important;
    }}
    
    /* Disable scrolling in sidebar content */
    section[data-testid="stSidebar"] .stVerticalBlock {{
        overflow-y: hidden !important;
        max-height: 100vh !important;
    }}
    
    /* Sidebar text */
    .css-1d391kg .element-container {{
        color: var(--text-primary) !important;
    }}
    
    /* Sidebar selectbox */
    .css-1d391kg .stSelectbox label {{
        color: var(--text-primary) !important;
    }}
    
    /* Main content area */
    .main .block-container {{
        background-color: var(--background-color) !important;
    }}
    
    /* App header */
    header[data-testid="stHeader"] {{
        background-color: var(--background-color) !important;
    }}
    
    /* Main app container */
    .stApp > header {{
        background-color: var(--background-color) !important;
    }}
    
    .stApp {{
        background-color: var(--background-color) !important;
    }}
    
    /* Professional tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: var(--surface-color);
        border-radius: 8px;
        padding: 0.25rem;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
    }}
    
    /* Theme toggle button */
    .theme-toggle {{
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 999;
        background: var(--surface-color);
        border: 1px solid var(--border-color);
        border-radius: 50%;
        width: 3rem;
        height: 3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        box-shadow: 0 2px 8px var(--shadow-color);
        transition: all 0.2s ease;
    }}
    
    .theme-toggle:hover {{
        transform: scale(1.1);
    }}
    
    /* Professional success/error messages */
    .success-message {{
        background-color: var(--accent-color);
        border: 1px solid var(--primary-color);
        border-radius: 8px;
        padding: 1rem;
        color: var(--primary-color);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }}
    
    .error-message {{
        background-color: #fef2f2;
        border: 1px solid #dc2626;
        border-radius: 8px;
        padding: 1rem;
        color: #dc2626;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }}
    
    /* Clean, professional spacing */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Remove default Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stDeployButton {{display:none;}}
    </style>
    """, unsafe_allow_html=True)


def initialize_database():
    """Initialize database connection"""
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    return st.session_state.db_manager


def format_currency(value: float, currency: str = "USD") -> str:
    """Format currency with thousand separators"""
    if value is None or pd.isna(value):
        return f"{currency} 0.00"
    return f"{currency} {value:,.2f}"


def format_number(value: float) -> str:
    """Format number with thousand separators"""
    if value is None or pd.isna(value):
        return "0"
    return f"{value:,.0f}" if value == int(value) else f"{value:,.2f}"


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header" style="position: relative; overflow: hidden;">
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.08; font-size: 8rem; font-weight: 800; color: white; pointer-events: none; z-index: 0;">
            IESL
        </div>
        <div style="position: relative; z-index: 1;">
            <h1>PO Dashboard</h1>
            <p>Strategic Business Unit Purchase Order Management System</p>
            <p style="font-size: 1rem; margin-top: 0.5rem; opacity: 0.9;"></p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, subtitle: str = "", delta: str = None):
    """Render a metric card"""
    delta_html = ""
    if delta:
        delta_html = f'<div class="metric-subtitle">{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subtitle">{subtitle}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def dashboard_page():
    """Main dashboard page"""
    st.title("Dashboard Overview")
    
    db_manager = st.session_state.db_manager
    
    # Exchange rate for USD to NGN
    USD_TO_NGN = 1463.0
    
    # Initialize currency preference in session state
    if 'currency_preference' not in st.session_state:
        st.session_state.currency_preference = 'USD'
    
    # Currency Toggle
    st.markdown("### Currency Display")
    col_toggle1, col_toggle2, col_toggle3 = st.columns([1, 1, 4])
    with col_toggle1:
        if st.button("$ USD", type="primary" if st.session_state.currency_preference == 'USD' else "secondary", use_container_width=True):
            st.session_state.currency_preference = 'USD'
            st.rerun()
    with col_toggle2:
        if st.button("₦ NGN", type="primary" if st.session_state.currency_preference == 'NGN' else "secondary", use_container_width=True):
            st.session_state.currency_preference = 'NGN'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get data
    try:
        total_summary = db_manager.get_total_summary()
        sbu_summary = db_manager.get_sbu_summary()
        recent_pos = db_manager.get_purchase_orders()
        expiring_pos = db_manager.get_expiring_pos(30)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Get selected currency
    selected_currency = st.session_state.currency_preference
    currency_symbol = "$" if selected_currency == "USD" else "₦"
    
    # Portfolio Overview Section
    st.subheader("Portfolio Overview")
    
    # Portfolio Overview - 4 Cards in Single Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate values based on selected currency
    total_value = total_summary.get('total_value') or 0
    avg_value = total_summary.get('avg_po_value') or 0
    
    if selected_currency == 'NGN':
        total_value = total_value * USD_TO_NGN
        avg_value = avg_value * USD_TO_NGN
    
    with col1:
        render_metric_card(
            "Active POs",
            str(total_summary.get('active_pos', 0)),
            "Currently running"
        )
    
    with col2:
        render_metric_card(
            "Total Portfolio Value",
            f"{currency_symbol}{total_value:,.2f}",
            selected_currency
        )
    
    with col3:
        render_metric_card(
            "Avg PO Value",
            f"{currency_symbol}{avg_value:,.0f}",
            f"Per purchase order"
        )
    
    with col4:
        render_metric_card(
            "Client Count",
            str(total_summary.get('total_clients', 0)),
            "Total clients"
        )
    
    # SBU Overview Section
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("SBU Overview")
    
    # Prepare SBU data mapping
    sbu_name_mapping = {
        "ENGINEERING, DESIGN AND CONSTRUCTION": "ED&C",
        "GLOBAL COMMERCIAL MANAGEMENT": "GCM",
        "OILFIELD SUPPLY AND SERVICES": "OSS",
        "PROJECT MANAGEMENT CONSULTANCY SERVICES": "PMC",
        "POWER & RENEWABLES": "P&R",
        "TECHNICAL CONSULTANCY SERVICES": "TCS"
    }
    
    sbu_data_map = {}
    if sbu_summary:
        for sbu in sbu_summary:
            full_name = sbu.get('name', '')
            shorthand = sbu_name_mapping.get(full_name, full_name)
            sbu_data_map[shorthand] = sbu
    
    target_sbus = ["ED&C", "GCM", "OSS", "PMC", "P&R", "TCS"]
    
    # Helper function to render compact SBU card
    def render_compact_sbu_card(sbu_code, sbu_data_map, selected_currency, USD_TO_NGN):
        if sbu_code in sbu_data_map:
            sbu_data = sbu_data_map[sbu_code]
            total_pos = sbu_data.get('total_pos', 0)
            total_value = sbu_data.get('total_value', 0) or 0
            
            if selected_currency == 'NGN':
                total_value = total_value * USD_TO_NGN
                currency_sym = "₦"
            else:
                currency_sym = "$"
            
            st.markdown(f"""
            <div class="metric-card" style="min-height: 100px; max-height: 110px; padding: 0.75rem 0.5rem;">
                <div class="metric-label" style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.25rem;">{sbu_code}</div>
                <div class="metric-value" style="font-size: 1.4rem; margin: 0.2rem 0;">{total_pos} POs</div>
                <div class="metric-subtitle" style="font-size: 0.75rem;">
                    {currency_sym}{total_value:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            currency_sym = "₦" if selected_currency == 'NGN' else "$"
            st.markdown(f"""
            <div class="metric-card" style="min-height: 100px; max-height: 110px; padding: 0.75rem 0.5rem;">
                <div class="metric-label" style="font-size: 0.85rem; font-weight: 700; margin-bottom: 0.25rem;">{sbu_code}</div>
                <div class="metric-value" style="font-size: 1.4rem; margin: 0.2rem 0;">0 POs</div>
                <div class="metric-subtitle" style="font-size: 0.75rem;">{currency_sym}0</div>
            </div>
            """, unsafe_allow_html=True)
    
    # SBU Cards - 3 rows x 2 columns
    # Row 1: ED&C, GCM
    col1, col2 = st.columns(2)
    with col1:
        render_compact_sbu_card(target_sbus[0], sbu_data_map, selected_currency, USD_TO_NGN)
    with col2:
        render_compact_sbu_card(target_sbus[1], sbu_data_map, selected_currency, USD_TO_NGN)
    
    # Row 2: OSS, PMC
    col1, col2 = st.columns(2)
    with col1:
        render_compact_sbu_card(target_sbus[2], sbu_data_map, selected_currency, USD_TO_NGN)
    with col2:
        render_compact_sbu_card(target_sbus[3], sbu_data_map, selected_currency, USD_TO_NGN)
    
    # Row 3: P&R, TCS
    col1, col2 = st.columns(2)
    with col1:
        render_compact_sbu_card(target_sbus[4], sbu_data_map, selected_currency, USD_TO_NGN)
    with col2:
        render_compact_sbu_card(target_sbus[5], sbu_data_map, selected_currency, USD_TO_NGN)
    
    # Risk Alert at the bottom
    if expiring_pos:
        st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
        col_alert, col_button = st.columns([5, 1])
        with col_alert:
            total_at_risk = sum(po['po_value'] for po in expiring_pos)
            if selected_currency == 'NGN':
                total_at_risk = total_at_risk * USD_TO_NGN
            
            st.markdown(f"""
            <div style="background-color: #854d0e; border-left: 4px solid #facc15; padding: 1rem; border-radius: 8px;">
                <div style="color: #fef3c7; font-weight: 600; margin-bottom: 0.25rem;">⚠️ Risk Alert</div>
                <div style="color: #fef3c7;">
                    <strong>{len(expiring_pos)} purchase orders</strong> worth <strong>{currency_symbol}{total_at_risk:,.2f}</strong> are expiring within 30 days!
                </div>
            </div>
            """, unsafe_allow_html=True)
        with col_button:
            if st.button("View Details", key="view_expiring_pos", use_container_width=True):
                st.session_state.current_page = "Analytics"
                st.rerun()
    
    # Recent Purchase Orders
    # st.subheader("Recent Purchase Orders")
    
    # if recent_pos:
    #     po_df = pd.DataFrame(recent_pos[:15])  # Show last 15 POs
        
    #     # Format the dataframe for display
    #     display_df = po_df[['po_number', 'sbu_name', 'client_name', 'po_value', 
    #                        'currency', 'start_date', 'expiry_date', 'status']].copy()
        
    #     # Format currency
    #     display_df['formatted_value'] = display_df.apply(
    #         lambda row: f"{row['currency']} {row['po_value']:,.2f}", axis=1
    #     )
        
    #     # Select and rename columns
    #     final_df = display_df[['po_number', 'sbu_name', 'client_name', 'formatted_value', 
    #                           'start_date', 'expiry_date', 'status']].copy()
    #     final_df.columns = ['PO Number', 'SBU', 'Client', 'Value', 'Start Date', 'Expiry Date', 'Status']
        
    #     # Column visibility control
    #     all_po_columns = list(final_df.columns)
    #     default_po_columns = ['PO Number', 'Client', 'Value', 'Start Date', 'Status']
        
    #     with st.expander("🔧 Column Visibility Settings", expanded=False):
    #         selected_po_columns = st.multiselect(
    #             "Select columns to display:",
    #             options=all_po_columns,
    #             default=[col for col in default_po_columns if col in all_po_columns],
    #             key="recent_pos_columns"
    #         )
        
    #     # Display only selected columns
    #     if selected_po_columns:
    #         st.dataframe(
    #             final_df[selected_po_columns],
    #             width="stretch",
    #             hide_index=True,
    #             use_container_width=True
    #         )
    #     else:
    #         st.warning("Please select at least one column to display.")
    # else:
    #     st.info("No recent purchase orders available.")


def data_entry_page():
    """Data entry page for NEW POs only"""
    st.title("Data Entry - Purchase Orders")
    
    db_manager = st.session_state.db_manager
    
    # Create tabs for PO entry types only (SBU and Client management removed)
    tab1, tab2 = st.tabs(["Purchase Order Entry", "PO Management"])
    
    with tab1:
        st.subheader("Add New Purchase Order")
        
        # Get data for dropdowns
        sbus = db_manager.get_sbus()
        clients = db_manager.get_clients()
        
        if not sbus:
            st.warning("No SBUs available. Please add SBUs first.")
            return
        
        if not clients:
            st.warning("No clients available. Please add clients first using the Client Entry tab.")
            return
        
        with st.form("po_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                po_number = st.text_input("PO Number *", placeholder="PO-2024-001")
                
                sbu_options = {sbu['name']: sbu['id'] for sbu in sbus}
                selected_sbu = st.selectbox("Strategic Business Unit *", list(sbu_options.keys()))
                
                client_options = {client['name']: client['id'] for client in clients}
                selected_client = st.selectbox("Client Company *", list(client_options.keys()))
                
                col_curr, col_val = st.columns([1, 3])
                with col_curr:
                    currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "CAD", "AUD"])
                with col_val:
                    po_value = st.number_input("PO Value *", min_value=0.01, step=1000.0, format="%.2f")
                
                if po_value > 0:
                    st.caption(f"💰 Formatted: {format_currency(po_value, currency)}")
                
                start_date = st.date_input("Start Date *", value=date.today())
                expiry_date = st.date_input("Expiry Date *", value=date.today() + timedelta(days=365))
            
            with col2:
                status = st.selectbox("Status", ["Active", "Pending", "On Hold", "Completed", "Cancelled"])
                
                project_name = st.text_input("Project Name", placeholder="Project identifier")
                
                project_description = st.text_area("Project Description", placeholder="Brief project description")
                
                contract_type = st.selectbox(
                    "Contract Type",
                    ["", "FEED (Front-End Engineering Design)",
                     "EPC (Engineering, Procurement, Construction)",
                     "EPCM (Engineering, Procurement, Construction Management)",
                     "Engineering Services Only", "Consulting Services",
                     "Maintenance Contract", "Equipment Supply", "Material Supply", "Other"]
                )
                
                risk_factor = st.selectbox(
                    "Risk Factor *",
                    [1, 2, 3, 4, 5],
                    index=2,
                    help="1 = Low Risk, 5 = High Risk"
                )
                st.caption("Risk Level: " + ["Low Risk", "Low-Medium Risk", "Medium Risk", "Medium-High Risk", "High Risk"][risk_factor - 1])
            
            submitted = st.form_submit_button("Save Purchase Order", type="primary")
            
            if submitted:
                # Validation
                errors = []
                if not po_number.strip():
                    errors.append("PO Number is required")
                if po_value <= 0:
                    errors.append("PO Value must be greater than 0")
                if start_date >= expiry_date:
                    errors.append("Start Date must be before Expiry Date")
                
                if errors:
                    for error in errors:
                        st.error(f"Error: {error}")
                else:
                    try:
                        po_id = db_manager.add_purchase_order(
                            po_number=po_number.strip(),
                            sbu_id=sbu_options[selected_sbu],
                            client_id=client_options[selected_client],
                            po_value=po_value,
                            currency=currency,
                            start_date=start_date.strftime("%Y-%m-%d"),
                            expiry_date=expiry_date.strftime("%Y-%m-%d"),
                            status=status,
                            project_name=project_name.strip(),
                            project_description=project_description.strip(),
                            contract_type=contract_type,
                            payment_terms="",
                            risk_factor=risk_factor
                        )
                        st.success(f"Purchase Order '{po_number}' saved successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving purchase order: {e}")
    
    with tab2:
        st.subheader("Manage Existing Purchase Orders")
        
        # Get existing purchase orders
        existing_pos = db_manager.get_purchase_orders()
        
        if not existing_pos:
            st.info("No purchase orders found. Add a purchase order using the 'Purchase Order Entry' tab.")
        else:
            # Add search/filter options
            st.write("**Filter Options:**")
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                filter_sbu = st.selectbox("Filter by SBU", ["All"] + list(set([po['sbu_name'] for po in existing_pos])))
            
            with filter_col2:
                filter_status = st.selectbox("Filter by Status", ["All", "Active", "Pending", "On Hold", "Completed", "Cancelled"])
            
            with filter_col3:
                filter_client = st.selectbox("Filter by Client", ["All"] + list(set([po['client_name'] for po in existing_pos])))
            
            # Apply filters
            filtered_pos = existing_pos
            if filter_sbu != "All":
                filtered_pos = [po for po in filtered_pos if po['sbu_name'] == filter_sbu]
            if filter_status != "All":
                filtered_pos = [po for po in filtered_pos if po['status'] == filter_status]
            if filter_client != "All":
                filtered_pos = [po for po in filtered_pos if po['client_name'] == filter_client]
            
            st.write(f"**Showing {len(filtered_pos)} of {len(existing_pos)} purchase orders:**")
            
            # Get data for dropdowns
            sbus = db_manager.get_sbus()
            clients = db_manager.get_clients()
            
            # Create expandable sections for each PO
            for i, po in enumerate(filtered_pos):
                with st.expander(f"PO: {po['po_number']} - {po['client_name']} ({po['status']}) - ${po['po_value']:,.2f}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Editable form for this PO
                        with st.form(f"edit_po_{po['id']}"):
                            col_po1, col_po2 = st.columns(2)
                            
                            with col_po1:
                                edit_po_number = st.text_input("PO Number", value=po['po_number'], key=f"edit_po_number_{po['id']}")
                                
                                # SBU dropdown - find current index
                                sbu_options = {sbu['name']: sbu['id'] for sbu in sbus}
                                sbu_names = list(sbu_options.keys())
                                current_sbu_idx = sbu_names.index(po['sbu_name']) if po['sbu_name'] in sbu_names else 0
                                edit_sbu = st.selectbox("Strategic Business Unit", sbu_names, index=current_sbu_idx, key=f"edit_po_sbu_{po['id']}")
                                
                                # Client dropdown - find current index
                                client_options = {client['name']: client['id'] for client in clients}
                                client_names = list(client_options.keys())
                                current_client_idx = client_names.index(po['client_name']) if po['client_name'] in client_names else 0
                                edit_client = st.selectbox("Client Company", client_names, index=current_client_idx, key=f"edit_po_client_{po['id']}")
                                
                                col_curr, col_val = st.columns([1, 3])
                                with col_curr:
                                    currencies = ["USD", "EUR", "GBP", "CAD", "AUD"]
                                    curr_idx = currencies.index(po['currency']) if po['currency'] in currencies else 0
                                    edit_currency = st.selectbox("Currency", currencies, index=curr_idx, key=f"edit_po_currency_{po['id']}")
                                with col_val:
                                    edit_po_value = st.number_input("PO Value", min_value=0.01, value=float(po['po_value']), step=1000.0, format="%.2f", key=f"edit_po_value_{po['id']}")
                                
                                if edit_po_value > 0:
                                    st.caption(f"💰 Formatted: {format_currency(edit_po_value, edit_currency)}")
                                
                                # Convert date strings to date objects
                                from datetime import datetime
                                start_date_obj = datetime.strptime(po['start_date'], "%Y-%m-%d").date()
                                expiry_date_obj = datetime.strptime(po['expiry_date'], "%Y-%m-%d").date()
                                
                                edit_start_date = st.date_input("Start Date", value=start_date_obj, key=f"edit_po_start_{po['id']}")
                                edit_expiry_date = st.date_input("Expiry Date", value=expiry_date_obj, key=f"edit_po_expiry_{po['id']}")
                            
                            with col_po2:
                                statuses = ["Active", "Pending", "On Hold", "Completed", "Cancelled"]
                                status_idx = statuses.index(po['status']) if po['status'] in statuses else 0
                                edit_status = st.selectbox("Status", statuses, index=status_idx, key=f"edit_po_status_{po['id']}")
                                
                                edit_project_name = st.text_input("Project Name", value=po.get('project_name', ''), key=f"edit_po_project_{po['id']}")
                                
                                edit_project_desc = st.text_area("Project Description", value=po.get('project_description', ''), key=f"edit_po_desc_{po['id']}")
                                
                                contract_types = ["", "FEED (Front-End Engineering Design)",
                                                "EPC (Engineering, Procurement, Construction)",
                                                "EPCM (Engineering, Procurement, Construction Management)",
                                                "Engineering Services Only", "Consulting Services",
                                                "Maintenance Contract", "Equipment Supply", "Material Supply", "Other"]
                                contract_idx = contract_types.index(po.get('contract_type', '')) if po.get('contract_type', '') in contract_types else 0
                                edit_contract_type = st.selectbox("Contract Type", contract_types, index=contract_idx, key=f"edit_po_contract_{po['id']}")
                                
                                # Get current risk factor, default to 3 if not set
                                current_risk = po.get('risk_factor', 3) or 3
                                edit_risk_factor = st.selectbox(
                                    "Risk Factor",
                                    [1, 2, 3, 4, 5],
                                    index=current_risk - 1,
                                    help="1 = Low Risk, 5 = High Risk",
                                    key=f"edit_po_risk_{po['id']}"
                                )
                                st.caption("Risk Level: " + ["Low Risk", "Low-Medium Risk", "Medium Risk", "Medium-High Risk", "High Risk"][edit_risk_factor - 1])
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("Save Changes", type="primary"):
                                    # Validation
                                    errors = []
                                    if not edit_po_number.strip():
                                        errors.append("PO Number is required")
                                    if edit_po_value <= 0:
                                        errors.append("PO Value must be greater than 0")
                                    if edit_start_date >= edit_expiry_date:
                                        errors.append("Start Date must be before Expiry Date")
                                    
                                    if errors:
                                        for error in errors:
                                            st.error(f"Error: {error}")
                                    else:
                                        try:
                                            # Update purchase order
                                            db_manager.update_purchase_order(
                                                po_id=po['id'],
                                                po_number=edit_po_number.strip(),
                                                sbu_id=sbu_options[edit_sbu],
                                                client_id=client_options[edit_client],
                                                po_value=edit_po_value,
                                                currency=edit_currency,
                                                start_date=edit_start_date.strftime("%Y-%m-%d"),
                                                expiry_date=edit_expiry_date.strftime("%Y-%m-%d"),
                                                status=edit_status,
                                                project_name=edit_project_name.strip(),
                                                project_description=edit_project_desc.strip(),
                                                contract_type=edit_contract_type,
                                                payment_terms="",
                                                risk_factor=edit_risk_factor
                                            )
                                            st.success(f"Purchase Order '{edit_po_number}' updated successfully!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error updating purchase order: {e}")
                    
                    with col2:
                        st.write("**Danger Zone**")
                        if st.button(f"Delete PO", key=f"delete_po_{po['id']}", type="secondary"):
                            try:
                                db_manager.delete_purchase_order(po['id'])
                                st.success(f"Purchase Order '{po['po_number']}' deleted successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting purchase order: {e}")


def analytics_page():
    """Advanced analytics page"""
    st.title("Advanced Analytics & Insights")
    
    db_manager = st.session_state.db_manager
    analytics_data = db_manager.get_analytics_data()
    sbu_summary = db_manager.get_sbu_summary()
    
    # SBU Data Visuals (moved from Dashboard)
    st.subheader("SBU Performance Visuals")
    
    if sbu_summary:
        sbu_df = pd.DataFrame(sbu_summary)
        
        # SBU Performance Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # SBU Portfolio Value Chart
            fig_value = px.bar(
                sbu_df, 
                x='name', 
                y='total_value',
                title='SBU Portfolio Value Comparison',
                labels={'name': 'SBU', 'total_value': 'Total Value (USD)'},
                color='total_value',
                color_continuous_scale='Greens'
            )
            fig_value.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_value, use_container_width=True)
        
        with col2:
            # SBU PO Count Chart
            fig_count = px.bar(
                sbu_df,
                x='name',
                y='total_pos',
                title='SBU Purchase Order Count',
                labels={'name': 'SBU', 'total_pos': 'Number of POs'},
                color='total_pos',
                color_continuous_scale='Blues'
            )
            fig_count.update_layout(
                xaxis_tickangle=-45,
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig_count, use_container_width=True)
        
        # Monthly Trends
        if analytics_data.get('monthly_trends'):
            st.subheader("Monthly Trends")
            
            trends_df = pd.DataFrame(analytics_data['monthly_trends'])
            trends_df['month'] = pd.to_datetime(trends_df['month'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_po_trend = px.line(
                    trends_df,
                    x='month',
                    y='pos_count',
                    title='Monthly PO Count Trend',
                    labels={'month': 'Month', 'pos_count': 'Number of POs'}
                )
                fig_po_trend.update_traces(line_color='#1e8449', line_width=3)
                st.plotly_chart(fig_po_trend, use_container_width=True)
            
            with col2:
                fig_value_trend = px.line(
                    trends_df,
                    x='month',
                    y='total_value',
                    title='Monthly Portfolio Value Trend',
                    labels={'month': 'Month', 'total_value': 'Total Value (USD)'}
                )
                fig_value_trend.update_traces(line_color='#27ae60', line_width=3)
                st.plotly_chart(fig_value_trend, use_container_width=True)
    else:
        st.info("No SBU performance data available.")
    
    # Risk Factor Analysis
    st.subheader("Risk Factor Analysis")
    
    # Get all POs with risk factor
    all_pos = db_manager.get_purchase_orders()
    
    if all_pos:
        pos_df = pd.DataFrame(all_pos)
        
        # Ensure risk_factor exists, default to 3 if missing
        if 'risk_factor' not in pos_df.columns:
            pos_df['risk_factor'] = 3
        else:
            pos_df['risk_factor'] = pos_df['risk_factor'].fillna(3).astype(int)
        
        # Calculate risk statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_risk_count = len(pos_df[pos_df['risk_factor'] >= 4])
            render_metric_card(
                "High Risk POs",
                str(high_risk_count),
                "Risk Factor 4-5"
            )
        
        with col2:
            medium_risk_count = len(pos_df[pos_df['risk_factor'] == 3])
            render_metric_card(
                "Medium Risk POs",
                str(medium_risk_count),
                "Risk Factor 3"
            )
        
        with col3:
            low_risk_count = len(pos_df[pos_df['risk_factor'] <= 2])
            render_metric_card(
                "Low Risk POs",
                str(low_risk_count),
                "Risk Factor 1-2"
            )
        
        # Risk Factor Distribution Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Risk Factor Distribution by Count
            risk_dist = pos_df.groupby('risk_factor').size().reset_index(name='count')
            risk_dist['risk_label'] = risk_dist['risk_factor'].map({
                1: "1 - Low Risk",
                2: "2 - Low-Medium",
                3: "3 - Medium",
                4: "4 - Medium-High",
                5: "5 - High Risk"
            })
            
            fig_risk_count = px.bar(
                risk_dist,
                x='risk_label',
                y='count',
                title='PO Count by Risk Factor',
                labels={'risk_label': 'Risk Level', 'count': 'Number of POs'},
                color='risk_factor',
                color_continuous_scale='RdYlGn_r'
            )
            fig_risk_count.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_risk_count, use_container_width=True)
        
        with col2:
            # Risk Factor Distribution by Value
            risk_value = pos_df.groupby('risk_factor')['po_value'].sum().reset_index()
            risk_value['risk_label'] = risk_value['risk_factor'].map({
                1: "1 - Low Risk",
                2: "2 - Low-Medium",
                3: "3 - Medium",
                4: "4 - Medium-High",
                5: "5 - High Risk"
            })
            
            fig_risk_value = px.bar(
                risk_value,
                x='risk_label',
                y='po_value',
                title='Portfolio Value by Risk Factor',
                labels={'risk_label': 'Risk Level', 'po_value': 'Total Value (USD)'},
                color='risk_factor',
                color_continuous_scale='RdYlGn_r'
            )
            fig_risk_value.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_risk_value, use_container_width=True)
        
        # Risk Factor by SBU
        st.subheader("Risk Distribution by SBU")
        risk_by_sbu = pos_df.groupby(['sbu_name', 'risk_factor']).size().reset_index(name='count')
        
        fig_risk_sbu = px.bar(
            risk_by_sbu,
            x='sbu_name',
            y='count',
            color='risk_factor',
            title='Risk Factor Distribution across SBUs',
            labels={'sbu_name': 'SBU', 'count': 'Number of POs', 'risk_factor': 'Risk Factor'},
            color_continuous_scale='RdYlGn_r',
            barmode='stack'
        )
        fig_risk_sbu.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig_risk_sbu, use_container_width=True)
    else:
        st.info("No purchase order data available for risk analysis.")
    
    # Expiry Risk Analysis
    st.subheader("Expiry Risk Analysis")
    
    days_ahead = st.selectbox("Analyze POs expiring within:", [7, 14, 30, 60, 90], index=2)
    expiring_pos = db_manager.get_expiring_pos(days_ahead)
    
    if expiring_pos:
        total_risk_value = sum(po['po_value'] for po in expiring_pos)
        
        col1, col2 = st.columns(2)
        with col1:
            render_metric_card(
                "Expiring POs",
                str(len(expiring_pos)),
                f"Within {days_ahead} days",
            )
        
        with col2:
            render_metric_card(
                "Value at Risk",
                f"${total_risk_value:,.2f}",
                "USD",
            )
        
        # Expiring POs table
        risk_df = pd.DataFrame(expiring_pos)
        display_risk = risk_df[['po_number', 'sbu_name', 'client_name', 'po_value', 
                               'expiry_date', 'days_remaining']].copy()
        display_risk.columns = ['PO Number', 'SBU', 'Client', 'Value (USD)', 'Expiry Date', 'Days Remaining']
        display_risk['Value (USD)'] = display_risk['Value (USD)'].apply(lambda x: f"${x:,.2f}")
        display_risk['Days Remaining'] = display_risk['Days Remaining'].astype(int)
        
        st.dataframe(
            display_risk,
            width="stretch",
            hide_index=True
        )
    else:
        st.success(f"No purchase orders expiring within {days_ahead} days!")
    
    # Client Analysis
    if analytics_data.get('top_clients'):
        st.subheader("Top Clients Analysis")
        
        clients_df = pd.DataFrame(analytics_data['top_clients'][:10])
        
        fig_clients = px.bar(
            clients_df,
            x='total_value',
            y='name',
            orientation='h',
            title='Top 10 Clients by Portfolio Value',
            labels={'total_value': 'Total Value (USD)', 'name': 'Client'},
            color='total_value',
            color_continuous_scale='Greens'
        )
        fig_clients.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_clients, use_container_width=True)
    
    # Status Distribution
    if analytics_data.get('status_distribution'):
        st.subheader("Status Distribution Analysis")
        
        status_df = pd.DataFrame(analytics_data['status_distribution'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_status_count = px.pie(
                status_df,
                values='count',
                names='status',
                title='PO Count by Status',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_status_count, use_container_width=True)
        
        with col2:
            fig_status_value = px.pie(
                status_df,
                values='total_value',
                names='status',
                title='Portfolio Value by Status',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_status_value, use_container_width=True)


def reports_page():
    """Reports and export page"""
    st.title("Reports & Data Export")
    
    db_manager = st.session_state.db_manager
    
    st.subheader("Quick Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("SBU Performance Report", width="stretch"):
            sbu_data = db_manager.get_sbu_summary()
            if sbu_data:
                st.subheader("SBU Performance Summary Report")
                
                sbu_df = pd.DataFrame(sbu_data)
                for col in ['total_value', 'avg_po_value']:
                    if col in sbu_df.columns:
                        sbu_df[col] = sbu_df[col].fillna(0).apply(lambda x: f"${(x or 0):,.2f}")
                
                st.dataframe(sbu_df, width="stretch", hide_index=True)
            else:
                st.warning("No SBU data available for report.")
        
        if st.button("Risk Assessment Report", width="stretch"):
            expiring_pos = db_manager.get_expiring_pos(30)
            if expiring_pos:
                st.subheader("Risk Assessment Report")
                
                total_risk = sum(po['po_value'] for po in expiring_pos)
                st.metric("Total Value at Risk", f"${total_risk:,.2f}")
                
                risk_df = pd.DataFrame(expiring_pos)
                st.dataframe(risk_df, width="stretch", hide_index=True)
            else:
                st.success("No immediate risks identified.")
    
    with col2:
        if st.button("Client Analysis Report", width="stretch"):
            analytics_data = db_manager.get_analytics_data()
            if analytics_data.get('top_clients'):
                st.subheader("Client Analysis Report")
                
                clients_df = pd.DataFrame(analytics_data['top_clients'])
                clients_df['total_value'] = clients_df['total_value'].apply(lambda x: f"${(x or 0):,.2f}")
                
                st.dataframe(clients_df, width="stretch", hide_index=True)
            else:
                st.warning("No client data available for report.")
        
        if st.button("Financial Summary Report", width="stretch"):
            total_summary = db_manager.get_total_summary()
            st.subheader("Financial Summary Report")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Portfolio Value", f"${(total_summary.get('total_value') or 0):,.2f}")
                st.metric("Total Purchase Orders", total_summary.get('total_pos', 0))
                st.metric("Active POs", total_summary.get('active_pos', 0))
            
            with col_b:
                st.metric("Average PO Value", f"${(total_summary.get('avg_po_value') or 0):,.2f}")
                st.metric("Completed POs", total_summary.get('completed_pos', 0))
                st.metric("Cancelled POs", total_summary.get('cancelled_pos', 0))
    
    # Data Export Section
    st.subheader("Data Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Export to Excel", width="stretch"):
            try:
                # Export detailed PO data
                po_df = db_manager.export_to_dataframe('purchase_orders_detailed')
                
                # Create download button
                @st.cache_data
                def convert_df_to_excel(df):
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, sheet_name='Purchase_Orders', index=False)
                        
                        # Add SBU summary
                        sbu_data = st.session_state.db_manager.get_sbu_summary()
                        if sbu_data:
                            sbu_df = pd.DataFrame(sbu_data)
                            sbu_df.to_excel(writer, sheet_name='SBU_Summary', index=False)
                    
                    return output.getvalue()
                
                excel_data = convert_df_to_excel(po_df)
                
                st.download_button(
                    label="Download Excel File",
                    data=excel_data,
                    file_name=f"po_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        if st.button("Generate Summary Report", width="stretch"):
            try:
                # Generate HTML report content
                total_summary = db_manager.get_total_summary()
                sbu_summary = db_manager.get_sbu_summary()
                expiring_pos = db_manager.get_expiring_pos(30)
                
                report_html = f"""
                <html>
                <head><title>PO Dashboard Report</title></head>
                <body>
                <h1>PO Dashboard Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h2>Executive Summary</h2>
                <ul>
                <li>Total Purchase Orders: {total_summary.get('total_pos', 0)}</li>
                <li>Total Portfolio Value: ${(total_summary.get('total_value') or 0):,.2f}</li>
                <li>Active POs: {total_summary.get('active_pos', 0)}</li>
                <li>Total Clients: {total_summary.get('total_clients', 0)}</li>
                </ul>
                
                <h2>Risk Analysis</h2>
                <p>Purchase orders expiring in next 30 days: {len(expiring_pos)}</p>
                
                </body>
                </html>
                """
                
                st.download_button(
                    label="Download HTML Report",
                    data=report_html,
                    file_name=f"po_report_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )
                
            except Exception as e:
                st.error(f"Report generation failed: {e}")


def landing_page():
    """Default landing page"""
    # Render the main header only on landing page
    render_header()
    
    # Welcome section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h2 style="color: var(--text-primary); margin-bottom: 1rem;">Welcome!</h2>
    
        </div>
        """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("### Quick Actions")
    
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)
    
    with action_col1:
        if st.button("View Dashboard", width="stretch", type="primary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
    
    with action_col2:
        if st.button("Data Entry", width="stretch"):
            st.session_state.current_page = "Data Entry"
            st.rerun()
    
    with action_col3:
        if st.button("Analytics", width="stretch"):
            st.session_state.current_page = "Analytics"
            st.rerun()
    
    with action_col4:
        if st.button("Reports", width="stretch"):
            st.session_state.current_page = "Reports"
            st.rerun()
    


def settings_page():
    """Settings and configuration page"""
    st.title("Settings")
    
    st.subheader("Theme Settings")
    
    # Theme toggle in settings
    col1, col2 = st.columns([3, 1])
    
    with col1:
        current_theme = "Dark Mode" if st.session_state.dark_mode else "Light Mode"
        st.write(f"**Current Theme:** {current_theme}")
        
        st.write("Choose your preferred theme for the dashboard interface:")
        
    with col2:
        theme_text = "Switch to Light" if st.session_state.dark_mode else "Switch to Dark"
        if st.button(theme_text, type="primary", width="stretch"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    
    st.markdown("---")
    
    # Theme preview
    st.subheader("Theme Preview")
    
    preview_col1, preview_col2 = st.columns(2)
    
    with preview_col1:
        st.markdown("**Light Theme**")
        st.markdown("""
        <div style="background: #ffffff; border: 1px solid #d5dbdb; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <div style="color: #1e8449; font-weight: 600; font-size: 1.1rem;">Clean & Professional</div>
            <div style="color: #2c3e50; margin-top: 0.5rem;">Perfect for bright environments and detailed work</div>
        </div>
        """, unsafe_allow_html=True)
    
    with preview_col2:
        st.markdown("**Dark Theme**")
        st.markdown("""
        <div style="background: #262730; border: 1px solid #4a4a4a; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
            <div style="color: #27ae60; font-weight: 600; font-size: 1.1rem;">Modern & Easy on Eyes</div>
            <div style="color: #fafafa; margin-top: 0.5rem;">Ideal for extended usage and low-light conditions</div>
        </div>
        """, unsafe_allow_html=True)


def main():
    """Main Streamlit application"""
    configure_page()
    
    # Initialize database
    db_manager = initialize_database()
    
    # Initialize page state if not exists
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    
    # Hide sidebar completely on homepage
    if st.session_state.current_page == "Home":
        # CSS to hide sidebar completely
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        .stApp > div:first-child {
            margin-left: 0px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Show sidebar navigation for all other pages
        st.sidebar.title("")
        
        # Navigation buttons in sidebar single column
        if st.sidebar.button("Home", width="stretch", type="primary" if st.session_state.current_page == "Home" else "secondary"):
            st.session_state.current_page = "Home"
            st.rerun()
        
        if st.sidebar.button("Dashboard", width="stretch", type="primary" if st.session_state.current_page == "Dashboard" else "secondary"):
            st.session_state.current_page = "Dashboard"
            st.rerun()
        
        if st.sidebar.button("Data Entry", width="stretch", type="primary" if st.session_state.current_page == "Data Entry" else "secondary"):
            st.session_state.current_page = "Data Entry"
            st.rerun()
        
        if st.sidebar.button("Analytics", width="stretch", type="primary" if st.session_state.current_page == "Analytics" else "secondary"):
            st.session_state.current_page = "Analytics"
            st.rerun()
        
        if st.sidebar.button("Reports", width="stretch", type="primary" if st.session_state.current_page == "Reports" else "secondary"):
            st.session_state.current_page = "Reports"
            st.rerun()
        
        if st.sidebar.button("Settings", width="stretch", type="primary" if st.session_state.current_page == "Settings" else "secondary"):
            st.session_state.current_page = "Settings"
            st.rerun()
        
        st.sidebar.markdown("---")
        
        # Add refresh button to sidebar
        if st.sidebar.button("Refresh Data", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    pages = {
        "Home": landing_page,
        "Dashboard": dashboard_page,
        "Data Entry": data_entry_page,
        "Analytics": analytics_page,
        "Reports": reports_page,
        "Settings": settings_page
    }
    
    selected_page = st.session_state.current_page
    
    # Add some sidebar info
    st.sidebar.markdown("---")
    st.sidebar.info("""
    **PO Dashboard v2.0**
    
    """)
    
    # Display selected page
    pages[selected_page]()


if __name__ == "__main__":
    main()
