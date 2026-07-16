import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Design Tokens
PRIMARY_BLUE = "#3b82f6"
PRIMARY_PURPLE = "#8b5cf6"
DARK_TEXT = "#1f2937"
LIGHT_BG = "#f3f4f6"
WHITE = "#ffffff"

def inject_custom_css():
    """
    Injects global CSS styling into the Streamlit app.
    Hides default sidebar routing to allow our customized navigation system
    and enforces the custom blue-purple gradient theme.
    """
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Page Structure */
    html, body, [data-testid="stAppViewContainer"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background-color: {LIGHT_BG};
        color: {DARK_TEXT};
    }}
    
    /* Hide standard Streamlit navigation in the sidebar */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}
    
    /* Custom Sidebar Styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    [data-testid="stSidebar"] * {{
        color: #e2e8f0 !important;
    }}
    
    /* Headers & Text Formatting */
    h1 {{
        color: #1e3a8a;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    h2, h3 {{
        color: #2563eb;
        font-weight: 600;
        margin-top: 1rem;
    }}
    
    /* Styled Cards */
    .dashboard-card {{
        background: linear-gradient(135deg, {WHITE} 0%, #f9fafb 100%);
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }}
    .dashboard-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1), 0 4px 6px -2px rgba(59, 130, 246, 0.05);
        border-color: #bfdbfe;
    }}
    
    .gradient-card-blue {{
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.2);
        margin-bottom: 1rem;
    }}
    .gradient-card-purple {{
        background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important;
        color: white !important;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
        margin-bottom: 1rem;
    }}
    
    /* Custom buttons and actions */
    div.stButton > button {{
        background: linear-gradient(135deg, {PRIMARY_BLUE} 0%, {PRIMARY_PURPLE} 100%);
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: auto;
    }}
    div.stButton > button:hover {{
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
        transform: scale(1.02);
        color: white !important;
    }}
    
    /* Custom secondary buttons e.g. for destructive actions */
    .destructive-btn div.stButton > button {{
        background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%) !important;
    }}
    .destructive-btn div.stButton > button:hover {{
        background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
        box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }}
    
    /* Text Inputs & Select Boxes styling */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {{
        border-radius: 8px !important;
    }}
    
    /* Adjust Streamlit default header spacing */
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
