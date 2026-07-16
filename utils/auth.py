import re
import bcrypt
import streamlit as st
from utils.database import load_json, add_user, USERS_FILE

def validate_email(email: str) -> bool:
    """
    Validates email format using regex.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def authenticate_user(username, password):
    """
    Checks if a username and password match any database user.
    Uses bcrypt to check hashed password.
    Returns (True, user_dict) or (False, error_message).
    """
    users = load_json(USERS_FILE, [])
    
    user = next((u for u in users if u["username"] == username), None)
    if not user:
        return False, "Invalid username or password."
        
    stored_hash = user.get("password")
    
    try:
        # Check bcrypt hash
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8")):
            return True, user
    except Exception:
        # Graceful handling if hashing check fails
        return False, "Authentication engine failure."
        
    return False, "Invalid username or password."

def register_user(name, email, username, password, confirm_password, role):
    """
    Registers a new user after validation.
    Returns (True, user_dict) or (False, error_message).
    """
    if not name or not email or not username or not password or not confirm_password:
        return False, "All fields are required."
        
    if not validate_email(email):
        return False, "Please enter a valid email address."
        
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    if password != confirm_password:
        return False, "Passwords do not match."
        
    # Check if role is valid
    if role not in ["Student", "Faculty", "Admin"]:
        return False, "Invalid user role selected."
        
    # Database level check & insert
    success, res = add_user(name, email, username, password, role)
    if success:
        return True, "User registered successfully!"
    else:
        return False, res

def init_session():
    """
    Initializes Streamlit session states for tracking authentication.
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "name" not in st.session_state:
        st.session_state.name = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "email" not in st.session_state:
        st.session_state.email = None

def login_session(user_dict):
    """
    Updates the session states to indicate successful login.
    """
    st.session_state.logged_in = True
    st.session_state.user_id = user_dict["id"]
    st.session_state.username = user_dict["username"]
    st.session_state.name = user_dict["name"]
    st.session_state.role = user_dict["role"]
    st.session_state.email = user_dict["email"]

def logout_session():
    """
    Clears current session states and triggers a reload.
    """
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.name = None
    st.session_state.role = None
    st.session_state.email = None
    # Use streamlit query parameters or experimental rerun to refresh state
    st.rerun()
