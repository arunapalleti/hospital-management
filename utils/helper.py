import streamlit as st
from utils.auth import logout_user

def render_header(page_title):
    """Renders a premium sticky header with active user details and a quick logout."""
    fullname = st.session_state.get("fullname", "Guest")
    role = st.session_state.get("role", "User")
    theme = st.session_state.get("theme", "light")
    
    theme_icon = "🌙" if theme == "light" else "☀️"
    
    html = f"""
    <div class="sticky-header">
        <div class="header-title">🏥 Smart Hospital / {page_title}</div>
        <div style="display: flex; align-items: center; gap: 16px;">
            <div class="status-badge badge-success" style="padding: 6px 12px;">
                👤 {fullname} ({role})
            </div>
            <div class="status-badge" style="background: rgba(2, 132, 199, 0.1); border: 1px solid rgba(2, 132, 199, 0.2); color: var(--accent-color); font-weight: 500;">
                🔔 Active Session
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_badge(status):
    """Returns HTML string for custom status badges."""
    status_lower = str(status).lower().strip()
    if status_lower in ["available", "active", "issued", "in stock", "success"]:
        return f'<span class="status-badge badge-success">{status}</span>'
    elif status_lower in ["on leave", "pending", "low stock", "expiring soon", "warning"]:
        return f'<span class="status-badge badge-warning">{status}</span>'
    else:  # out of stock, danger, inactive, error
        return f'<span class="status-badge badge-danger">{status}</span>'

def render_global_search():
    """Renders a global search bar in the page and filters a query."""
    st.text_input("🔍 Search globally (patients, doctors, or tablets)...", key="global_search_query")
