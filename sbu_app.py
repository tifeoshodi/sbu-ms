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
        page_title="SBU/PO Dashboard - Oil & Gas Engineering",
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
        padding: 1.5rem 1rem;
        border-radius: 12px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px var(--shadow-color);
        text-align: center;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }}
    
    .metric-card:hover {{
        border-color: var(--primary-color);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px var(--shadow-color);
    }}
    
    .metric-value {{
        font-family: 'Inter', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0.5rem 0;
        line-height: 1.2;
        word-break: break-word;
    }}
    
    .metric-label {{
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    
    .metric-subtitle {{
        font-family: 'Inter', sans-serif;
        font-size: 0.75rem;
        font-weight: 500;
        color: var(--text-secondary);
        margin-top: 0.5rem;
        opacity: 0.8;
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


def render_header():
    """Render the main header"""
    st.markdown("""
    <div class="main-header">
        <h1>SBU/PO Dashboard</h1>
        <p>Strategic Business Unit & Purchase Order Management System</p>
        <p style="font-size: 1rem; margin-top: 0.5rem; opacity: 0.9;"></p>
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
    
    # Get data
    try:
        total_summary = db_manager.get_total_summary()
        sbu_summary = db_manager.get_sbu_summary()
        recent_pos = db_manager.get_purchase_orders()
        expiring_pos = db_manager.get_expiring_pos(30)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return
    
    # Executive Summary - Metrics in columns
    st.subheader("Executive Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_metric_card(
            "Total Purchase Orders",
            str(total_summary.get('total_pos', 0)),
            "All time"
        )
        
        render_metric_card(
            "Average PO Value",
            f"${(total_summary.get('avg_po_value') or 0):,.2f}",
            "USD"
        )
    
    with col2:
        render_metric_card(
            "Total Portfolio Value",
            f"${(total_summary.get('total_value') or 0):,.2f}",
            "USD"
        )
        
        render_metric_card(
            "Active SBU",
            str(total_summary.get('active_sbus', 0)),
            "Business units"
        )
    
    with col3:
        render_metric_card(
            "Active PO",
            str(total_summary.get('active_pos', 0)),
            "Currently running"
        )
        
        render_metric_card(
            "Total Clients",
            str(total_summary.get('total_clients', 0)),
            "Companies"
        )
    
    # Expiring POs Alert
    if expiring_pos:
        st.warning(f"**Alert**: {len(expiring_pos)} purchase orders worth ${sum(po['po_value'] for po in expiring_pos):,.2f} are expiring within 30 days!")
    
    # SBU Performance Summary
    st.subheader("SBU Performance Summary")
    
    if sbu_summary:
        sbu_df = pd.DataFrame(sbu_summary)
        
        # Format currency columns
        for col in ['total_value', 'avg_po_value']:
            if col in sbu_df.columns:
                sbu_df[col] = sbu_df[col].fillna(0).apply(lambda x: f"${(x or 0):,.2f}")
        
        # Rename columns for display
        display_columns = {
            'name': 'SBU',
            'manager': 'Manager',
            'total_pos': 'Total POs',
            'total_value': 'Total Value (USD)',
            'active_pos': 'Active',
            'completed_pos': 'Completed',
            'cancelled_pos': 'Cancelled',
            'avg_po_value': 'Avg PO Value'
        }
        
        sbu_df_display = sbu_df.rename(columns=display_columns)
        sbu_df_display['Manager'] = sbu_df_display['Manager'].fillna('Not assigned')
        
        st.data_editor(
            sbu_df_display,
            width="stretch",
            hide_index=True,
            use_container_width=True,
            disabled=True
        )
        
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
    else:
        st.info("No SBU performance data available.")
    
    # Recent Purchase Orders
    st.subheader("Recent Purchase Orders")
    
    if recent_pos:
        po_df = pd.DataFrame(recent_pos[:15])  # Show last 15 POs
        
        # Format the dataframe for display
        display_df = po_df[['po_number', 'sbu_name', 'client_name', 'po_value', 
                           'currency', 'start_date', 'expiry_date', 'status']].copy()
        
        # Format currency
        display_df['formatted_value'] = display_df.apply(
            lambda row: f"{row['currency']} {row['po_value']:,.2f}", axis=1
        )
        
        # Select and rename columns
        final_df = display_df[['po_number', 'sbu_name', 'client_name', 'formatted_value', 
                              'start_date', 'expiry_date', 'status']].copy()
        final_df.columns = ['PO Number', 'SBU', 'Client', 'Value', 'Start Date', 'Expiry Date', 'Status']
        
        st.dataframe(
            final_df,
            width="stretch",
            hide_index=True
        )
    else:
        st.info("No recent purchase orders available.")
    
    # Analytics Charts
    analytics_data = db_manager.get_analytics_data()
    
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


def data_entry_page():
    """Data entry page for clients and POs"""
    st.title("Data Entry")
    
    db_manager = st.session_state.db_manager
    
    # Create tabs for different entry types
    tab1, tab2, tab3, tab4 = st.tabs(["SBU Entry", "SBU Management", "Client Entry", "Purchase Order Entry"])
    
    with tab1:
        st.subheader("Add New Strategic Business Unit")
        
        with st.form("sbu_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                sbu_name = st.text_input("SBU Name *", placeholder="e.g., Engineering")
                manager_name = st.text_input("Manager Name", placeholder="e.g., Ola Rotimi")
                # department = st.selectbox("Department", [
                    # "Upstream Engineering",
                    # "Midstream Engineering", 
                    # "Downstream Engineering",
                    # "Digital Solutions",
                    # "Environmental Engineering",
                    # "Project Management",
                    # "Other"
                # ])
            
            with col2:
                location = st.text_input("Location", placeholder="e.g., Lagos, NG")
                budget = st.number_input("Annual Budget (USD)", min_value=0.0, value=0.0, step=1000.0)
                description = st.text_area("Description", placeholder="Brief description of SBU activities...")
            
            submitted = st.form_submit_button("Add SBU", type="primary")
            
            if submitted:
                if not sbu_name.strip():
                    st.error("SBU name is required!")
                else:
                    try:
                        # Check if SBU already exists
                        existing_sbus = db_manager.get_sbus()
                        existing_names = [sbu['name'].lower() for sbu in existing_sbus]
                        
                        if sbu_name.strip().lower() in existing_names:
                            st.warning(f"SBU '{sbu_name}' already exists in the database.")
                        else:
                            sbu_id = db_manager.add_sbu(
                                name=sbu_name.strip(),
                                manager=manager_name.strip() if manager_name.strip() else "TBD",
                                # department=department,
                                location=location.strip(),
                                budget=budget,
                                description=description.strip()
                            )
                            st.success(f"SBU '{sbu_name}' added successfully!")
                            st.rerun()
                    except Exception as e:
                        if "UNIQUE constraint" in str(e):
                            st.warning(f"SBU '{sbu_name}' already exists in the database.")
                        else:
                            st.error(f"Error adding SBU: {e}")
    
    with tab3:
        st.subheader("Add New Client Company")
        
        with st.form("client_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name *", placeholder="Enter client company name")
                industry_sector = st.selectbox(
                    "Industry Sector",
                    ["", "Oil & Gas Upstream", "Oil & Gas Midstream", "Oil & Gas Downstream",
                     "Petrochemicals", "Renewable Energy", "Mining", "Power Generation",
                     "Manufacturing", "Other"]
                )
                contact_person = st.text_input("Contact Person", placeholder="Primary contact name")
                email = st.text_input("Email", placeholder="contact@company.com")
            
            with col2:
                phone = st.text_input("Phone", placeholder="+1-234-567-8900")
                address = st.text_area("Address", placeholder="Company address")
                country = st.selectbox(
                    "Country",
                    ["", "United States", "Canada", "United Kingdom", "Norway", "Netherlands",
                     "Saudi Arabia", "UAE", "Qatar", "Kuwait", "Nigeria", "Brazil", 
                     "Mexico", "Australia", "Indonesia", "Malaysia", "China", "India", 
                     "Russia", "Other"]
                )
            
            submitted = st.form_submit_button("Add Client", type="primary")
            
            if submitted:
                if not company_name.strip():
                    st.error("Company name is required!")
                else:
                    try:
                        # Check if client already exists
                        existing_clients = db_manager.get_clients()
                        existing_names = [client['name'].lower() for client in existing_clients]
                        
                        if company_name.strip().lower() in existing_names:
                            st.warning(f"Client '{company_name}' already exists in the database.")
                        else:
                            client_id = db_manager.add_client(
                                name=company_name.strip(),
                                industry_sector=industry_sector,
                                contact_person=contact_person.strip(),
                                email=email.strip(),
                                phone=phone.strip(),
                                address=address.strip(),
                                country=country
                            )
                            st.success(f"Client '{company_name}' added successfully!")
                            st.rerun()
                    except Exception as e:
                        if "UNIQUE constraint" in str(e):
                            st.warning(f"Client '{company_name}' already exists in the database.")
                        else:
                            st.error(f"Error adding client: {e}")
    
    with tab2:
        st.subheader("Manage Existing SBUs")
        
        # Get existing SBUs
        existing_sbus = db_manager.get_sbus()
        
        if not existing_sbus:
            st.info("No SBUs found. Add an SBU using the 'SBU Entry' tab.")
        else:
            st.write("**Select an SBU to edit or remove:**")
            
            # Create columns for the SBU list
            for i, sbu in enumerate(existing_sbus):
                with st.expander(f"SBU: {sbu['name']} (Manager: {sbu['manager']})"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        # Editable form for this SBU
                        with st.form(f"edit_sbu_{sbu['id']}"):
                            edit_name = st.text_input("SBU Name", value=sbu['name'], key=f"edit_name_{sbu['id']}")
                            edit_manager = st.text_input("Manager", value=sbu['manager'], key=f"edit_manager_{sbu['id']}")
                            edit_description = st.text_area("Description", value=sbu.get('description', ''), key=f"edit_desc_{sbu['id']}")
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                if st.form_submit_button("Save Changes", type="primary"):
                                    try:
                                        # Update SBU
                                        import sqlite3
                                        with sqlite3.connect(db_manager.db_path) as conn:
                                            cursor = conn.cursor()
                                            cursor.execute("""
                                                UPDATE sbu SET name = ?, manager = ?, description = ?
                                                WHERE id = ?
                                            """, (edit_name, edit_manager, edit_description, sbu['id']))
                                            conn.commit()
                                        
                                        st.success(f"SBU '{edit_name}' updated successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error updating SBU: {e}")
                    
                    with col2:
                        st.write("**Danger Zone**")
                        if st.button(f"Delete SBU", key=f"delete_{sbu['id']}", type="secondary"):
                            # Check if SBU has associated POs
                            pos = db_manager.get_purchase_orders()
                            has_pos = any(po['sbu_id'] == sbu['id'] for po in pos)
                            
                            if has_pos:
                                st.error("Cannot delete SBU: It has associated Purchase Orders. Delete those first.")
                            else:
                                try:
                                    import sqlite3
                                    with sqlite3.connect(db_manager.db_path) as conn:
                                        cursor = conn.cursor()
                                        cursor.execute("DELETE FROM sbu WHERE id = ?", (sbu['id'],))
                                        conn.commit()
                                    
                                    st.success(f"SBU '{sbu['name']}' deleted successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error deleting SBU: {e}")
    
    with tab4:
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
                     "Maintenance Contract", "Other"]
                )
                
                payment_terms = st.text_input("Payment Terms", placeholder="e.g., Net 30, 50% upfront")
            
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
                            payment_terms=payment_terms.strip()
                        )
                        st.success(f"Purchase Order '{po_number}' saved successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error saving purchase order: {e}")


def analytics_page():
    """Advanced analytics page"""
    st.title("Advanced Analytics & Insights")
    
    db_manager = st.session_state.db_manager
    analytics_data = db_manager.get_analytics_data()
    
    # Risk Analysis
    st.subheader("Risk Analysis")
    
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
    
    col1, col2, col3 = st.columns(3)
    
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
                    file_name=f"sbu_po_export_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col2:
        if st.button("Export to CSV", width="stretch"):
            try:
                po_df = db_manager.export_to_dataframe('purchase_orders_detailed')
                
                csv_data = po_df.to_csv(index=False)
                
                st.download_button(
                    label="Download CSV File",
                    data=csv_data,
                    file_name=f"sbu_po_export_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
            except Exception as e:
                st.error(f"Export failed: {e}")
    
    with col3:
        if st.button("Generate Summary Report", width="stretch"):
            try:
                # Generate HTML report content
                total_summary = db_manager.get_total_summary()
                sbu_summary = db_manager.get_sbu_summary()
                expiring_pos = db_manager.get_expiring_pos(30)
                
                report_html = f"""
                <html>
                <head><title>SBU/PO Dashboard Report</title></head>
                <body>
                <h1>SBU/PO Dashboard Report</h1>
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
                    file_name=f"sbu_po_report_{datetime.now().strftime('%Y%m%d')}.html",
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
        st.sidebar.title("Navigation")
        
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
    **SBU/PO Dashboard v2.0**
    
    Built with Streamlit for better usability and responsive design.
    
    **Features:**
    - Real-time data visualization
    - Interactive charts and tables  
    - Professional reporting
    - Data export capabilities
    """)
    
    # Display selected page
    pages[selected_page]()


if __name__ == "__main__":
    main()
