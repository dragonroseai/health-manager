import datetime as dt
import pandas as pd
import streamlit as st

def show_measurement_selection(df):
    # Show selection of measurements to display.
    df_pivot = df.pivot_table(index="Date", columns="Name", values="Value", aggfunc="mean")

    def select_measurements(measurements, rerun=True):
        selected = []
        for measurement in measurements:
            if measurement in df_pivot.columns: selected += [measurement]
        st.session_state["measure_selection"] = selected
        if rerun: st.rerun()  # Rerun the app to reflect the change

    if "measure_selection" not in st.session_state:
        # st.session_state["measure_selection"] = ["Cholesterol"]  # Default selected for demo purposes
        select_measurements(["Weight", "Cholesterol", "Triglycerides", "HDL", "LDL", "Glucose"], rerun=False)

    names = st.multiselect("Measurements", df.Name.unique(), st.session_state["measure_selection"])
    st.session_state["measure_selection"] = names  # Update session state with selected measurements

    # Add a row of buttons below measurement selection
    btn_cols = st.columns([5,5,5,5,5,5])
    with btn_cols[0]: btn0 = st.button("Weight lbs")
    with btn_cols[1]: btn1 = st.button("Weight %")
    with btn_cols[2]: btn2 = st.button("Weight Etc")
    with btn_cols[3]: btn3 = st.button("Lipid Panel")
    with btn_cols[4]: btn4 = st.button("Keto")
    with btn_cols[5]: btn5 = st.button("Blood Pressure")

    # Handle button clicks to update measurement selection
    if btn0:
        select_measurements(["Weight", "Body Fat", "Subcutaneous Fat", "Visceral Fat", 
            "Muscle Mass", "Skeletal Muscle", "Bone Mass", "Protein", "Body Water"])
    elif btn1:
        select_measurements(["Body Fat %", "Subcutaneous Fat %", "Visceral Fat %", 
            "Muscle Mass %", "Skeletal Muscle %", "Bone Mass %", "Protein %", "Body Water %"])
    elif btn2:
        select_measurements(["Weight", "BMI", "Visceral Fat Index", "BMR", "Metabolic Age"])
    elif btn3:
        select_measurements(["Cholesterol", "Triglycerides", "HDL", "LDL", "TC-HDL", "TC/HDL"])
    elif btn4:
        select_measurements(["Glucose", "Ketone", "Dr. Boz Ratio"])
    elif btn5:
        select_measurements(["Systolic", "Diastolic", "Pulse"])

    return names

def select_start_date(start_date, rerun=True):
    st.session_state["start_date"] = start_date
    if rerun: st.rerun()  # Rerun the app to reflect the change

def show_date_selection(df):
    if df.empty:
        max_date = pd.to_datetime(dt.date.today())
        min_date = max_date - pd.DateOffset(months=6)
    else:
        max_date = df["Date"].max()
        min_date = df["Date"].min()
    # Show start date and end date selection.
    if "start_date" not in st.session_state: 
        select_start_date((max_date - pd.DateOffset(months=6)).date(), rerun=False)

    #start_date = st.date_input("Start date", dt.date(2024,11,1))  # Default start date for demo purposes
    #start_date = st.date_input("Start date", df["Date"].min())
    #start_date = st.date_input("Start date", df["Date"].max() - pd.DateOffset(years=1))

    btn_cols = st.columns([5,5,1,5])
    with btn_cols[0]: start_date = st.date_input("Start date", st.session_state["start_date"])
    with btn_cols[1]: end_date = st.date_input("End date", max_date)
    with btn_cols[3]: st.write(""); st.write(""); show_ma = st.checkbox("1M Moving Avg")
    btn_cols = st.columns(6)
    with btn_cols[0]: btn0 = st.button("All Time")
    with btn_cols[1]: btn1 = st.button("2 Years")
    with btn_cols[2]: btn2 = st.button("1 Year")
    with btn_cols[3]: btn3 = st.button("6 Months")
    with btn_cols[4]: btn4 = st.button("3 Months")
    with btn_cols[5]: btn5 = st.button("1 Month")

    # Handle button clicks to update start_date
    if btn0: select_start_date(min_date.date())
    elif btn1: select_start_date((max_date - pd.DateOffset(years=2)).date())
    elif btn2: select_start_date((max_date - pd.DateOffset(years=1)).date())
    elif btn3: select_start_date((max_date - pd.DateOffset(months=6)).date())
    elif btn4: select_start_date((max_date - pd.DateOffset(months=3)).date())
    elif btn5: select_start_date((max_date - pd.DateOffset(months=1)).date())

    return start_date, end_date, show_ma