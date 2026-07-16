import streamlit as st
from utils.auth import register_user
from utils.styles import inject_custom_css
from utils.validation import (
    validate_non_empty,
    validate_email,
    validate_password_strength
)

# Initialize styling
inject_custom_css()

st.markdown("""
    <style>
    .register-container {
        max-width: 500px;
        margin: 0 auto;
        padding-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>Register New Staff</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-muted); margin-bottom: 24px;'>Create an administrative or clinical provider account.</p>", unsafe_allow_html=True)

with st.form("register_form"):
    fullname = st.text_input("Full Name", placeholder="e.g., Dr. Jane Smith")
    username = st.text_input("Username", placeholder="e.g., janesmith")
    email = st.text_input("Email Address", placeholder="e.g., jane.smith@hospital.com")
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Password", type="password", placeholder="••••••••")
    with col2:
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
        
    role = st.selectbox("Role", ["Doctor", "Admin"])
    
    submit = st.form_submit_button("Register Account")
    
    if submit:
        # Field validation
        fn_ok, fn_msg = validate_non_empty(fullname, "Full Name")
        u_ok, u_msg = validate_non_empty(username, "Username")
        e_ok, e_msg = validate_email(email)
        p_ok, p_msg = validate_password_strength(password)
        
        if not fn_ok:
            st.error(fn_msg)
        elif not u_ok:
            st.error(u_msg)
        elif not e_ok:
            st.error(e_msg)
        elif not p_ok:
            st.error(p_msg)
        elif password != confirm_password:
            st.error("Passwords do not match. Please re-enter passwords.")
        else:
            with st.spinner("Creating account..."):
                success, msg = register_user(fullname, username, email, password, role)
                if success:
                    st.success(f"Success! Account for {fullname} created as {role}. You can now log in.")
                else:
                    st.error(msg)
