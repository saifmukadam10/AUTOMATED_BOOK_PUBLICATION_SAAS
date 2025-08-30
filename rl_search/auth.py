# auth.py
import os
import streamlit as st
from supabase import create_client, Client

def _get_keys():
    # Prefer Streamlit secrets → then env vars
    url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
    key = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY"))
    if not url or not key:
        raise RuntimeError(
            "Supabase keys missing. Set SUPABASE_URL and SUPABASE_ANON_KEY "
            "in .streamlit/secrets.toml or environment variables."
        )
    return url, key

@st.cache_resource
def get_supabase() -> Client:
    url, key = _get_keys()
    return create_client(url, key)

def current_user():
    # Cached in session_state for UI speed
    return st.session_state.get("sb_user")

def login(email: str, password: str):
    sb = get_supabase()
    res = sb.auth.sign_in_with_password({"email": email, "password": password})
    st.session_state["sb_user"] = res.user
    st.session_state["sb_session"] = res.session
    return res.user

def signup(email: str, password: str):
    sb = get_supabase()
    res = sb.auth.sign_up({"email": email, "password": password})
    return res

def signout():
    sb = get_supabase()
    try:
        sb.auth.sign_out()
    finally:
        st.session_state.pop("sb_user", None)
        st.session_state.pop("sb_session", None)

def require_auth_ui():
    """Call at the top of Streamlit page. Renders auth UI if not logged in."""
    user = current_user()
    if user:
        return user

    st.title("🔐 Sign in to continue")
    tab_login, tab_signup = st.tabs(["Login", "Create account"])

    with tab_login:
        e = st.text_input("Email", key="login_email")
        p = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            try:
                u = login(e, p)
                st.success(f"Welcome {u.email}!")
                st.experimental_rerun()
            except Exception as ex:
                st.error(f"Login failed: {ex}")

    with tab_signup:
        e2 = st.text_input("Email (new)", key="signup_email")
        p2 = st.text_input("Password (new)", type="password", key="signup_pass")
        if st.button("Create account"):
            try:
                signup(e2, p2)
                st.success("Account created. Please log in.")
            except Exception as ex:
                st.error(f"Signup failed: {ex}")

    st.stop()  # Prevent the rest of the app from rendering for unauthenticated users
