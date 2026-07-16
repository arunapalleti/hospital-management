import streamlit as st
from utils.auth import logout_user

# Log user out immediately and redirect
logout_user()
