import streamlit as st
import os
from PIL import Image

def require_auth(allowed_roles=None):
    """
    Checks if user is logged in and belongs to allowed roles.
    If not logged in, redirects back to app.py.
    """
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("🔒 Access Denied. Please log in first.")
        st.switch_page("app.py")
        st.stop()
        
    if allowed_roles and st.session_state.role not in allowed_roles:
        st.error(f"🚫 Access Denied. This section requires {', '.join(allowed_roles)} privileges.")
        st.stop()

def load_image_safely(relative_path: str, fallback_color: str = "#3b82f6"):
    """
    Loads PIL image. If not found, returns None.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    full_path = os.path.join(base_dir, relative_path)
    
    if os.path.exists(full_path):
        try:
            return Image.open(full_path)
        except Exception:
            return None
    return None

def custom_banner(title: str, subtitle: str):
    """
    Renders a modern gradient title banner at the top of a workspace page.
    """
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%); 
                    padding: 2.5rem; border-radius: 16px; margin-bottom: 2rem; color: white;">
            <h1 style="color: white; margin: 0; font-size: 2.2rem; font-weight: 800; letter-spacing: -0.05rem;">{title}</h1>
            <p style="color: rgba(255, 255, 255, 0.9); margin-top: 0.5rem; margin-bottom: 0; font-size: 1.1rem; font-weight: 400;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
