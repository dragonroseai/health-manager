import streamlit as st

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]: return True

    with st.form("Login"):
        st.write("Please log in to access the Health Manager.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        if submitted:
            # Simple hardcoded credentials (replace with secure method in production)
            if (username == "hiangswee" and password == "health21") \
                or (username == "khinfoun" and password == "health21"):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    return False