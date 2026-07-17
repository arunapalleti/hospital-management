import os
import streamlit as st
from dotenv import load_dotenv
from utils.database import initialize_databases

# Load environment variables
load_dotenv()

# Set up page configurations
st.set_page_config(
    page_title="Smart Hospital Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database JSON files on startup
initialize_databases()

# Manage theme setting in session state (default to light mode)
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

# Authentication and routing setup
is_authenticated = st.session_state.get("authenticated", False)

# Define application pages mapping
if not is_authenticated:
    # Pages visible when not logged in
    login_page = st.Page("pages/login.py", title="Login", icon="🔑")
    register_page = st.Page("pages/register.py", title="Register", icon="📝")
    pg = st.navigation({
        "Authentication": [login_page, register_page]
    })
else:
    # Pages visible when logged in
    dashboard_page = st.Page("pages/dashboard.py", title="Dashboard", icon="🏥")
    patients_page = st.Page("pages/patients.py", title="Patients", icon="👤")
    doctors_page = st.Page("pages/doctors.py", title="Doctors", icon="👨‍⚕️")
    tablets_page = st.Page("pages/tablets.py", title="Tablets", icon="💊")
    recommendation_page = st.Page("pages/recommendation.py", title="Recommendations", icon="🩺")
    history_page = st.Page("pages/history.py", title="History", icon="📜")
    reports_page = st.Page("pages/reports.py", title="Reports", icon="📊")
    settings_page = st.Page("pages/settings.py", title="Settings", icon="⚙️")
    logout_page = st.Page("pages/logout.py", title="Logout", icon="🚪")
    
    pg = st.navigation({
        "Medical Console": [
            dashboard_page,
            patients_page,
            doctors_page,
            tablets_page,
            recommendation_page,
            history_page,
            reports_page,
            settings_page,
            logout_page
        ]
    })

# Run navigation router
pg.run()
