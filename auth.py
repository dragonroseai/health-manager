import json
import os
import pandas as pd
import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]: return True

    mode = st.radio("", ["Login", "Sign Up"], horizontal=True)
    if mode == "Login":
        login()
    elif mode == "Sign Up":
        signup()

    return False

# --- User Login Screen ---
def login():
    #st.write("<h3>Login</h3>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    if login_btn:
        users = pd.read_csv("data/users.csv")
        user_row = users[users["email"] == email]
        if not user_row.empty:
            pw = user_row.iloc[0]["password"]
            if password == pw:
                st.session_state["authenticated"] = True
                st.session_state["email"] = email
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid email or password.")
        else:
            st.error("Invalid email or password.")

# --- User Sign Up Screen ---
def signup():
    #st.write("<h2>Sign Up</h2>", unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")
    signup_btn = st.button("Create Account")
    if signup_btn:
        if not email or not password:
            st.error("Email and password are required.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            # Save new user (append to users.csv)
            users_file = "data/users.csv"
            if not os.path.exists(users_file):
                pd.DataFrame([{"email": email, "password": password}]).to_csv(users_file, index=False)
            else:
                users = pd.read_csv(users_file)
                if email in users["email"].values:
                    st.error("Email already exists.")
                    return
                users = pd.concat([users, pd.DataFrame([{"email": email, "password": password}])], ignore_index=True)
                users.to_csv(users_file, index=False)
            os.makedirs(f"data/{email}", exist_ok=True)
            health_data_file = f"data/{email}/health_data.csv"
            if not os.path.exists(health_data_file):
                pd.DataFrame(columns=["Name", "Value", "Units", "Date", "Note"]).to_csv(health_data_file, index=False)
            st.success("Account created! Please log in.")
            st.stop()