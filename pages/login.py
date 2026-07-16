import streamlit as st
from utils.auth import login_user
from utils.styles import inject_custom_css
from utils.validation import validate_non_empty

# Initialize styling
inject_custom_css()

# Center alignment styling
st.markdown("""
    <style>
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding-top: 40px;
        text-align: center;
    }
    .brand-logo {
        margin-bottom: 20px;
        filter: drop-shadow(0px 4px 10px rgba(0, 102, 204, 0.15));
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-container">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>Sign in to Smart Hospital</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); margin-bottom: 30px;'>Enter your credentials to access your administrative medical console.</p>", unsafe_allow_html=True)

# Login Form Container
with st.form("login_form", clear_on_submit=False):
    username = st.text_input("Username", placeholder="e.g., admin", key="login_username_input")
    password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password_input")
    
    submit_button = st.form_submit_button("Access Console")
    
    if submit_button:
        # Validate inputs
        u_ok, u_msg = validate_non_empty(username, "Username")
        p_ok, p_msg = validate_non_empty(password, "Password")
        
        if not u_ok:
            st.error(u_msg)
        elif not p_ok:
            st.error(p_msg)
        else:
            with st.spinner("Authenticating credentials..."):
                success = login_user(username, password)
                if success:
                    st.success(f"Access granted! Welcome, {st.session_state['fullname']}.")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

st.markdown("<p style='text-align: center; margin-top: 20px; color: var(--text-muted);'>Forgot credentials? Contact system support at support@smarthospital.com.</p>", unsafe_allow_html=True)
