import streamlit as st

def get_theme_colors(theme):
    """Returns CSS variable configurations for light or dark themes."""
    if theme == "dark":
        return {
            "bg_color": "#0f172a",
            "card_bg": "rgba(30, 41, 59, 0.7)",
            "card_border": "rgba(255, 255, 255, 0.08)",
            "text_color": "#f8fafc",
            "text_muted": "#94a3b8",
            "accent_color": "#0ea5e9",
            "accent_hover": "#38bdf8",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#ef4444",
            "shadow": "0 8px 32px 0 rgba(0, 0, 0, 0.3)"
        }
    else:  # Light mode default
        return {
            "bg_color": "#f8fafc",
            "card_bg": "rgba(255, 255, 255, 0.8)",
            "card_border": "rgba(15, 23, 42, 0.06)",
            "text_color": "#0f172a",
            "text_muted": "#64748b",
            "accent_color": "#0284c7",
            "accent_hover": "#0369a1",
            "success": "#10b981",
            "warning": "#d97706",
            "danger": "#dc2626",
            "shadow": "0 8px 32px 0 rgba(31, 38, 135, 0.07)"
        }

def inject_custom_css():
    """Injects high-fidelity custom CSS styles into the Streamlit app based on session theme."""
    theme = st.session_state.get("theme", "light")
    c = get_theme_colors(theme)
    
    # Custom scrollbar and standard overrides
    css = f"""
    <style>
    /* Root Variables */
    :root {{
        --bg-color: {c["bg_color"]};
        --card-bg: {c["card_bg"]};
        --card-border: {c["card_border"]};
        --text-color: {c["text_color"]};
        --text-muted: {c["text_muted"]};
        --accent-color: {c["accent_color"]};
        --accent-hover: {c["accent_hover"]};
        --success-color: {c["success"]};
        --warning-color: {c["warning"]};
        --danger-color: {c["danger"]};
        --card-shadow: {c["shadow"]};
    }}
    
    /* Global Styles */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: var(--bg-color) !important;
        color: var(--text-color) !important;
        font-family: 'Inter', 'Outfit', sans-serif !important;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: { "#1e293b" if theme == "light" else "#0b0f19" } !important;
        border-right: 1px solid var(--card-border) !important;
    }}
    
    /* Modern Glassmorphic Cards */
    .glass-card {{
        background: var(--card-bg) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: var(--card-shadow) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 20px !important;
    }}
    
    .glass-card:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 12px 40px 0 rgba(2, 132, 199, 0.15) !important;
        border-color: var(--accent-color) !important;
    }}
    
    /* Animated Metric Cards */
    .metric-container {{
        display: flex;
        align-items: center;
        gap: 16px;
    }}
    
    .metric-icon-box {{
        background: rgba(2, 132, 199, 0.1) !important;
        color: var(--accent-color) !important;
        border-radius: 12px !important;
        width: 48px !important;
        height: 48px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 24px !important;
        transition: all 0.3s ease !important;
    }}
    
    .glass-card:hover .metric-icon-box {{
        background: var(--accent-color) !important;
        color: white !important;
        transform: scale(1.1) rotate(5deg) !important;
    }}
    
    .metric-title {{
        font-size: 14px !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
        margin: 0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    
    .metric-value {{
        font-size: 28px !important;
        font-weight: 700 !important;
        color: var(--text-color) !important;
        margin: 4px 0 0 0 !important;
        line-height: 1 !important;
    }}
    
    /* Badges */
    .status-badge {{
        display: inline-flex !important;
        align-items: center !important;
        padding: 4px 10px !important;
        border-radius: 9999px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
    }}
    
    .badge-success {{
        background-color: rgba(16, 185, 129, 0.1) !important;
        color: var(--success-color) !important;
        border: 1px solid rgba(16, 185, 129, 0.2) !important;
    }}
    
    .badge-warning {{
        background-color: rgba(245, 158, 11, 0.1) !important;
        color: var(--warning-color) !important;
        border: 1px solid rgba(245, 158, 11, 0.2) !important;
    }}
    
    .badge-danger {{
        background-color: rgba(239, 68, 68, 0.1) !important;
        color: var(--danger-color) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
    }}
    
    /* Header Section */
    .sticky-header {{
        display: flex !important;
        justify-content: space-between !important;
        align-items: center !important;
        padding: 16px 24px !important;
        background: var(--card-bg) !important;
        border-bottom: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        margin-bottom: 24px !important;
        backdrop-filter: blur(8px) !important;
    }}
    
    .header-title {{
        margin: 0 !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        color: var(--accent-color) !important;
    }}
    
    /* Custom buttons override */
    div.stButton > button {{
        background: linear-gradient(135deg, var(--accent-color) 0%, #0369a1 100%) !important;
        color: white !important;
        border: none !important;
        padding: 8px 20px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.2) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }}
    
    div.stButton > button:hover {{
        background: linear-gradient(135deg, var(--accent-hover) 0%, var(--accent-color) 100%) !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.35) !important;
        transform: translateY(-2px) !important;
    }}
    
    div.stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    /* Custom forms cards styling */
    .stForm {{
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: var(--card-shadow) !important;
    }}
    
    /* Input Styling override */
    div[data-baseweb="input"], div[data-baseweb="select"], div[data-baseweb="textarea"] {{
        border-radius: 10px !important;
    }}
    
    /* Alerts and success cards */
    .element-container div.stAlert {{
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }}
    
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_metric_card(title, value, icon="🏥", tooltip=""):
    """Helper to render a beautiful metric card in the UI."""
    html = f"""
    <div class="glass-card" title="{tooltip}">
        <div class="metric-container">
            <div class="metric-icon-box">{icon}</div>
            <div>
                <p class="metric-title">{title}</p>
                <h3 class="metric-value">{value}</h3>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
