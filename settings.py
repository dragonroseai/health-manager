import datetime as dt
import json
import pandas as pd
import streamlit as st

def load_settings():
    try:
        with open(f"data/{st.session_state['email']}/settings.json", "r") as f:
            settings = json.load(f)
        return settings
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def show():
    settings = load_settings()

    if "settings_msg" in st.session_state:
        st.info(st.session_state["settings_msg"])
        del st.session_state["settings_msg"]

    st.markdown("<b>Settings</b>", unsafe_allow_html=True)
    with st.form("Settings"):
        height = st.text_input("Height", settings["height"] if "height" in settings else "",
                               help="Enter your height in inches. This will be used for BMI calculations.")  
        submitted = st.form_submit_button("Save")

    if submitted:
        try:
            settings["height"] = float(height)
            with open(f"data/{st.session_state['email']}/settings.json", "w") as f:
                json.dump(settings, f, indent=4)
            st.success("Settings saved!")
        except ValueError:
            st.error(f"Invalid {height}. Please enter valid number.")
