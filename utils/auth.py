import streamlit as st
from utils.database import load_data, save_data, hash_password

def verify_credentials(username, password):
    """Verifies user credentials. Returns the user dict if valid, else None."""
    users = load_data("users")
    hashed_pwd = hash_password(password)
    for user in users:
        if user.get("username").lower() == username.lower() and user.get("password") == hashed_pwd:
            return user
    return None

def login_user(username, password):
    """Logs the user in by establishing session states."""
    user = verify_credentials(username, password)
    if user:
        st.session_state["authenticated"] = True
        st.session_state["username"] = user["username"]
        st.session_state["fullname"] = user["fullname"]
        st.session_state["role"] = user["role"]
        st.session_state["email"] = user["email"]
        return True
    return False

def register_user(fullname, username, email, password, role):
    """Registers a new user after verifying uniqueness. Returns (Success, Message)."""
    users = load_data("users")
    
    # Check if username or email already exists
    for user in users:
        if user.get("username").lower() == username.lower():
            return False, "Username is already taken."
        if user.get("email").lower() == email.lower():
            return False, "Email is already registered."
            
    new_user = {
        "fullname": fullname,
        "username": username,
        "email": email,
        "password": hash_password(password),
        "role": role
    }
    
    users.append(new_user)
    if save_data("users", users):
        return True, "Registration successful!"
    return False, "An error occurred while saving. Please try again."

def logout_user():
    """Logs out the user and clears session state."""
    keys_to_clear = ["authenticated", "username", "fullname", "role", "email"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def update_user_password(username, old_password, new_password):
    """Changes password for the user if the old password is correct. Returns (Success, Message)."""
    users = load_data("users")
    hashed_old = hash_password(old_password)
    hashed_new = hash_password(new_password)
    
    for user in users:
        if user.get("username").lower() == username.lower():
            if user.get("password") != hashed_old:
                return False, "Incorrect old password."
            
            user["password"] = hashed_new
            if save_data("users", users):
                return True, "Password updated successfully!"
            return False, "Error saving new password."
            
    return False, "User not found."

def check_auth():
    """Security guard. Ensures user is authenticated, else blocks execution."""
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in to access this page.")
        st.stop()
