import streamlit as st
import os
import base64
from utils.config import inject_custom_css
from utils.database import init_database
from utils.auth import init_session, authenticate_user, register_user, login_session
from utils.helpers import load_image_safely

# Set page config
st.set_page_config(
    page_title="SmartCampusAI - Portal",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize JSON tables and folders
init_database()

# Initialize session structures
init_session()

# Inject Global CSS styling rules
inject_custom_css()

# Set Background Image if available
bg_img = load_image_safely("assets/background.jpg")
if bg_img:
    try:
        bg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "background.jpg"))
        with open(bg_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            [data-testid="stAppViewContainer"] {{
                background: linear-gradient(135deg, rgba(243, 244, 246, 0.85) 0%, rgba(229, 231, 235, 0.85) 100%), 
                            url("data:image/jpeg;base64,{encoded_string}") !important;
                background-size: cover !important;
                background-position: center !important;
                background-attachment: fixed !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        pass

# Redirect if already logged in
if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Dashboard.py")
    st.stop()

# Logo header
logo_img = load_image_safely("assets/logo.png")
col1, col2, col3 = st.columns([1, 1.2, 1])
with col2:
    if logo_img:
        st.image(logo_img, use_column_width=True)
    else:
        st.markdown(
            "<h1 style='text-align: center; font-size: 3rem;'>🎓</h1>", 
            unsafe_allow_html=True
        )

st.markdown(
    """
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='font-size: 2.2rem; background: linear-gradient(135deg, #1e3a8a 0%, #7c3aed 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            SmartCampusAI
        </h1>
        <p style='color: #4b5563; font-size: 1rem;'>AI-Powered Education Management Portal</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Authentication Panel Cards
tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

with tab1:
    st.markdown("### Sign In")
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username", key="login_username").strip()
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
        submit_login = st.form_submit_button("Authenticate")
        
        if submit_login:
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                success, res = authenticate_user(username, password)
                if success:
                    login_session(res)
                    st.success(f"Welcome back, {res['name']}!")
                    st.switch_page("pages/1_Dashboard.py")
                else:
                    st.error(res)

with tab2:
    st.markdown("### Create Account")
    with st.form("register_form", clear_on_submit=False):
        fullname = st.text_input("Full Name", placeholder="e.g. Jane Doe", key="reg_fullname").strip()
        email = st.text_input("Email", placeholder="e.g. jane@example.com", key="reg_email").strip()
        username = st.text_input("Username", placeholder="e.g. janedoe123", key="reg_username").strip()
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            password = st.text_input("Password", type="password", placeholder="At least 6 characters", key="reg_password")
        with col_p2:
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Verify password", key="reg_confirm_password")
            
        role = st.selectbox("Role", ["Student", "Faculty", "Admin"], index=0, key="reg_role")
        
        submit_register = st.form_submit_button("Register User")
        
        if submit_register:
            success, message = register_user(fullname, email, username, password, confirm_password, role)
            if success:
                st.success(message + " Please switch to the 'Login' tab to sign in.")
            else:
                st.error(message)
