import streamlit as st
from utils.auth import check_auth, update_user_password, logout_user
from utils.database import load_data
from utils.styles import inject_custom_css
from utils.helper import render_header
from utils.validation import validate_password_strength

# Protect access
check_auth()

# Inject styling
inject_custom_css()

# Header
render_header("System Settings")

st.markdown("### ⚙️ Administrative Console Settings")
st.markdown("Configure system visual styles, modify staff credentials, or inspect active diagnosis rules.")

# Settings panels
col_set1, col_set2 = st.columns(2)

with col_set1:
    # 1. Theme Configuration
    st.markdown("""
    <div class="glass-card" style="padding: 20px !important;">
        <h4 style="color: var(--accent-color); margin-top:0; margin-bottom:12px;">🎨 Theme Customization</h4>
        <p style="font-size:13px; color: var(--text-muted);">Adjust the color scheme of the hospital management dashboards.</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_theme = st.session_state.get("theme", "light")
    theme_choice = st.selectbox(
        "Choose Dashboard Theme Mode",
        options=["Light Mode", "Dark Mode"],
        index=0 if current_theme == "light" else 1,
        key="theme_mode_selector"
    )
    
    # Save selection and rerun
    selected_theme = "light" if theme_choice == "Light Mode" else "dark"
    if selected_theme != current_theme:
        st.session_state["theme"] = selected_theme
        st.success(f"Applying {theme_choice} layout configuration...")
        st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 2. Logout Actions
    st.markdown("""
    <div class="glass-card" style="padding: 20px !important;">
        <h4 style="color: var(--danger-color); margin-top:0; margin-bottom:12px;">🚪 Secure Session Close</h4>
        <p style="font-size:13px; color: var(--text-muted);">Logs out immediately, clearing session cache files from memory.</p>
    </div>
    """, unsafe_allow_html=True)
    
    logout_btn = st.button("Close Active Session & Logout", type="primary")
    if logout_btn:
        logout_user()


with col_set2:
    # 3. Change password credentials
    st.markdown("""
    <div class="glass-card" style="padding: 20px !important;">
        <h4 style="color: var(--accent-color); margin-top:0; margin-bottom:12px;">🔒 Security Profile Updates</h4>
        <p style="font-size:13px; color: var(--text-muted);">Reset the login password credentials for your active account profile.</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("change_password_form"):
        username = st.session_state.get("username", "admin")
        st.text_input("Active Username", value=username, disabled=True)
        
        old_pwd = st.text_input("Old Password", type="password", placeholder="••••••••")
        new_pwd = st.text_input("New Password", type="password", placeholder="••••••••")
        confirm_pwd = st.text_input("Confirm New Password", type="password", placeholder="••••••••")
        
        submit_btn = st.form_submit_button("Update Access Credentials")
        
        if submit_btn:
            if not old_pwd or not new_pwd:
                st.error("Please fill in all password fields.")
            elif new_pwd != confirm_pwd:
                st.error("New passwords do not match.")
            else:
                pwd_ok, pwd_msg = validate_password_strength(new_pwd)
                if not pwd_ok:
                    st.error(pwd_msg)
                else:
                    with st.spinner("Modifying secure credential keys..."):
                        success, msg = update_user_password(username, old_pwd, new_pwd)
                        if success:
                            st.success("Credentials updated! Logging out in 3 seconds to apply...")
                            import time
                            time.sleep(3)
                            logout_user()
                        else:
                            st.error(msg)

st.markdown("---")

# 4. View Diagnostic Rules Configured
st.markdown("### 📋 Active Diagnosis Matching Configurations")
st.markdown("These rules guide the diagnosis algorithm recommendation engines on matching symptoms to formulas:")

recs = load_data("recommendations")
if not recs:
    st.info("No recommendation rules defined in system configuration.")
else:
    for idx, rule in enumerate(recs):
        with st.expander(f"🩺 Rule #{idx + 1}: {rule.get('disease')} - Specialist: {rule.get('specialist')}"):
            st.markdown(f"""
            - **Target Disease**: {rule.get('disease')}
            - **Symptom Clues**: {", ".join(rule.get('symptoms', []))}
            - **Recommended Pills**: {", ".join(rule.get('tablets', []))}
            - **Standard Daily Dosage**: {rule.get('dosage')}
            - **Clinical Precautions**: {rule.get('precautions')}
            - **Side Effects**: {rule.get('side_effects')}
            """)
