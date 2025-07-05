import altair as alt
import datetime as dt
import pandas as pd
import streamlit as st

# --- Simple authentication setup ---
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

if not check_password(): st.stop()
#st.session_state["username"] = "hiangswee"  # Default username for demo purposes
# --- End authentication setup ---

# Show the page title and description.
st.set_page_config(page_title="Health Manager", page_icon="❤️")
st.title("Health Manager ❤️")
st.write(
    """
    This app visualizes your health data. Just click on the widgets below to explore!
    """
)

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
#@st.cache_data
def load_data():
    df = pd.read_csv(f"data/{st.session_state['username']}/health_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])  # Convert 'date' column to datetime
    return df

df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
df_pivot = df.pivot_table(
    index="Date", columns="Name", values="Value", aggfunc="mean"
)

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

preset_order = [
    "Date", "Weight", "BMI", 
    "Body Fat", "Body Fat %", "Subcutaneous Fat", "Subcutaneous Fat %", "Visceral Fat", "Visceral Fat %", "Visceral Fat Index",
    "Muscle Mass", "Muscle Mass %", "Skeletal Muscle", "Skeletal Muscle %", "Bone Mass", "Bone Mass %", 
    "Protein", "Protein %", "Body Water", "Body Water %", "BMR", "Metabolic Age",
    "Cholesterol", "Triglycerides", "HDL", "LDL", "TC-HDL", "TC/HDL", 
    "Glucose", "Ketone", "Dr. Boz Ratio", 
    "Systolic", "Diastolic", "Pulse",
    "Uric Acid", "Haematocrit", "Haemoglobin",
]

# Add a row of buttons below measurement selection
btn_cols = st.columns([1,5,1,5,1,5,1,5,1])
with btn_cols[1]: btn1 = st.button("Weight")
with btn_cols[3]: btn2 = st.button("Cholesterol")
with btn_cols[5]: btn3 = st.button("Keto")
with btn_cols[7]: btn4 = st.button("Blood Pressure")

# Handle button clicks to update measurement selection
if btn1:
    select_measurements(["Weight", "BMI", 
        "Body Fat", "Body Fat %", "Subcutaneous Fat", "Subcutaneous Fat %", "Visceral Fat", "Visceral Fat %", "Visceral Fat Index", 
        "Muscle Mass", "Muscle Mass %", "Skeletal Muscle", "Skeletal Muscle %", "Bone Mass", "Bone Mass %", 
        "Protein", "Protein %", "Body Water", "Body Water %", "BMR", "Metabolic Age"])
elif btn2:
    select_measurements(["Cholesterol", "Triglycerides", "HDL", "LDL", "TC-HDL", "TC/HDL"])
elif btn3:
    select_measurements(["Glucose", "Ketone", "Dr. Boz Ratio"])
elif btn4:
    select_measurements(["Systolic", "Diastolic", "Pulse"])

def select_start_date(start_date, rerun=True):
    st.session_state["start_date"] = start_date
    if rerun: st.rerun()  # Rerun the app to reflect the change

if "start_date" not in st.session_state: 
    select_start_date((df["Date"].max() - pd.DateOffset(months=6)).date(), rerun=False)

col1, col2 = st.columns(2)
with col1: 
    #start_date = st.date_input("Start date", dt.date(2024,11,1))  # Default start date for demo purposes
    #start_date = st.date_input("Start date", df["Date"].min())
    #start_date = st.date_input("Start date", df["Date"].max() - pd.DateOffset(years=1))
    start_date = st.date_input("Start date", st.session_state["start_date"])
with col2: 
    end_date = st.date_input("End date", df["Date"].max())

# Add a row of buttons below start date
btn_cols = st.columns([1,4,1,4,1,4,1,4,1])
with btn_cols[1]: btn1 = st.button("All Time")
with btn_cols[3]: btn2 = st.button("Last 2 Years")
with btn_cols[5]: btn3 = st.button("Last 1 Year")
with btn_cols[7]: btn4 = st.button("Last 6 Months")

# Handle button clicks to update start_date
if btn1: select_start_date(df["Date"].min().date())
elif btn2: select_start_date((df["Date"].max() - pd.DateOffset(years=2)).date())
elif btn3: select_start_date((df["Date"].max() - pd.DateOffset(years=1)).date())
elif btn4: select_start_date((df["Date"].max() - pd.DateOffset(months=6)).date())

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    (df["Name"].isin(names)) &
    (df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)))
]
df_reshaped = df_filtered.pivot_table(
    index="Date", columns="Name", values="Value", aggfunc="mean"
)
df_reshaped = df_reshaped.sort_index().ffill()
df_reshaped = df_reshaped.sort_values(by="Date", ascending=False)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="Date", var_name="Name", value_name="Value"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Date:T"), # axis=alt.Axis(format="%Y-%m-%d")
        y=alt.Y("Value:Q"),
        color=alt.Color("Name:N", legend=alt.Legend(title="Measurement", orient="bottom")),  # Legend at bottom
    )
    .properties(height=600)
)
st.altair_chart(chart, use_container_width=True)

# Display the data as a table using `st.dataframe`.
df_display = df_reshaped.copy()
df_display.index = df_display.index.strftime("%Y-%m-%d")  # Format index if 'date' is index
df_display = df_display.reset_index()
for col in df_display.columns:
    if col != "Date":
        df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
desired_order = []
for col in preset_order:
    if col in df_display.columns:
        desired_order.append(col)  # Append any preset columns that are not already in desired order
for col in df_display.columns:
    if col not in desired_order:
        desired_order.append(col)  # Append any other columns that are not in the desired order
st.dataframe(
    df_display[desired_order],
    use_container_width=True,
    hide_index=True,  # Hide the index column
)

record_types = [
    "Weight Bdy_Fat Skl_Msc Msc_Mss Prt BMR Sub_Fat Vis_Fat Bdy_Wtr Bon_Mss Mtb_Age",
    "Weight",
    "Systolic Diastolic Pulse",
    "Glucose Ketone",
    "Glucose",
    "Ketone",
    "Cholesterol Triglycerides HDL LDL",
    "Cholesterol",
    "Uric Acid",
    "Glucose Haematocrit Haemoglobin",
]

units = {
    "Weight": "lbs",
    "BMR": "kcal",
    "Systolic": "mmHg",
    "Diastolic": "mmHg",
    "Pulse": "Beats/min",
    "Glucose": "mg/dL",
    "Ketone": "mmol/L",
    "Cholesterol": "mg/dL",
    "Triglycerides": "mg/dL",
    "HDL": "mg/dL",
    "LDL": "mg/dL",
    "Uric Acid": "mg/dL",
    "Haematocrit": "%",
    "Haemoglobin": "g/dL",
}

with st.form("Add new record"):
    new_date = st.date_input("Date")
    new_time = st.time_input("Time")  
    new_type = st.selectbox("Name", record_types)
    new_value = st.text_input("Value(s)")  
    new_note = st.text_input("Note (optional)")  
    submitted = st.form_submit_button("Add")

if submitted:
    try:
        names = new_type.split(" ")
        values = [float(v) for v in new_value.split(" ")]
        kvs = dict(zip(names, values))
        new_date = dt.datetime.combine(new_date, new_time)  # Combine date and time
        new_date = pd.to_datetime(new_date)
        if new_type == "Weight Bdy_Fat Skl_Msc Msc_Mss Prt BMR Sub_Fat Vis_Fat Bdy_Wtr Bon_Mss Mtb_Age":
            if len(values) != 11:
                st.error("Please enter all 11 values for Weight Body_Fat Skeletal_Muscle Muscle_Mass Protein BMR Subcutaneous_Fat Visceral_Fat Body_Water Bone_Mass and Metabolic_Age.")
                st.stop()
            # weight = body_fat + muscle_mass + bone_mass
            weight = { "Date": new_date, "Name": "Weight", "Value": kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            bmi = { "Date": new_date, "Name": "BMI", "Value": kvs["Weight"]*703 / (5*12+6)**2, "Units": "", "Note": new_note }
            body_fat = { "Date": new_date, "Name": "Body Fat", "Value": kvs["Bdy_Fat"]*kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            body_fat_pct = { "Date": new_date, "Name": "Body Fat %", "Value": kvs["Bdy_Fat"], "Units": "%", "Note": new_note }
            subcutaneous_fat = { "Date": new_date, "Name": "Subcutaneous Fat", "Value": kvs["Sub_Fat"]*kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            subcutaneous_fat_pct = { "Date": new_date, "Name": "Subcutaneous Fat %", "Value": kvs["Sub_Fat"], "Units": "%", "Note": new_note }
            visceral_fat = { "Date": new_date, "Name": "Visceral Fat", "Value": (kvs["Bdy_Fat"]-kvs["Sub_Fat"])*kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            visceral_fat_pct = { "Date": new_date, "Name": "Visceral Fat %", "Value": kvs["Bdy_Fat"]-kvs["Sub_Fat"], "Units": "%", "Note": new_note }
            visceral_fat_index = { "Date": new_date, "Name": "Visceral Fat Index", "Value": kvs["Vis_Fat"], "Units": "", "Note": new_note }
            muscle_mass = { "Date": new_date, "Name": "Muscle Mass", "Value": kvs["Msc_Mss"], "Units": units["Weight"], "Note": new_note }
            muscle_mass_pct = { "Date": new_date, "Name": "Muscle Mass %", "Value": kvs["Msc_Mss"]/kvs["Weight"], "Units": "%", "Note": new_note }
            skeletal_muscle = { "Date": new_date, "Name": "Skeletal Muscle", "Value": kvs["Skl_Msc"]*kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            skeletal_muscle_pct = { "Date": new_date, "Name": "Skeletal Muscle %", "Value": kvs["Skl_Msc"], "Units": "%", "Note": new_note }
            bone_mass = { "Date": new_date, "Name": "Bone Mass", "Value": kvs["Bon_Mss"], "Units": units["Weight"], "Note": new_note }
            bone_mass_pct = { "Date": new_date, "Name": "Bone Mass %", "Value": kvs["Bon_Mss"]/kvs["Weight"], "Units": "%", "Note": new_note }
            protein = { "Date": new_date, "Name": "Protein", "Value": kvs["Prt"]*kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            protein_pct = { "Date": new_date, "Name": "Protein %", "Value": kvs["Prt"], "Units": "%", "Note": new_note }
            body_water = { "Date": new_date, "Name": "Body Water", "Value": kvs["Bdy_Wtr"]*kvs["Weight"], "Units": units["Weight"], "Note": new_note }
            body_water_pct = { "Date": new_date, "Name": "Body Water %", "Value": kvs["Bdy_Wtr"], "Units": "%", "Note": new_note }
            bmr = { "Date": new_date, "Name": "BMR", "Value": kvs["BMR"], "Units": units["BMR"], "Note": new_note }
            metabolic_age = { "Date": new_date, "Name": "Metabolic Age", "Value": kvs["Mtb_Age"], "Units": "Year", "Note": new_note }
            df = pd.concat([df, pd.DataFrame([weight, bmi, body_fat, body_fat_pct, subcutaneous_fat, subcutaneous_fat_pct, \
                                              visceral_fat, visceral_fat_pct, visceral_fat_index, muscle_mass, muscle_mass_pct, \
                                              skeletal_muscle, skeletal_muscle_pct, bone_mass, bone_mass_pct, protein, protein_pct, \
                                              body_water, body_water_pct, bmr, metabolic_age])], ignore_index=True)   
        else:
            rows = []
            for name, value in kvs.items():
                if name not in units: units[name] = ""  # Default unit if not specified
                rows.append({ "Date": new_date, "Name": name, "Value": value, "Units": units[name], "Note": new_note })
            if "Weight" in names: # BMI = weight in lbs x 703 / (height in inches)^2
                rows.append({ "Date": new_date, "Name": "BMI", "Value": kvs["Weight"]*703 / (5*12+6)**2, "Units": "", "Note": new_note })
            if "Glucose" in names and "Ketone" in names:
                rows.append({ "Date": new_date, "Name": "Dr. Boz Ratio", "Value": kvs["Glucose"]/kvs["Ketone"], "Units": "", "Note": new_note })
            if "Cholesterol" in names and "HDL" in names:
                rows.append({ "Date": new_date, "Name": "TC-HDL", "Value": kvs["TC"]-kvs["HDL"], "Units": units["Cholesterol"], "Note": new_note })
                rows.append({ "Date": new_date, "Name": "TC/HDL", "Value": kvs["TC"]/kvs["HDL"], "Units": "", "Note": new_note })
            df = pd.concat([df, pd.DataFrame(rows)], ignore_index=True)
        df.to_csv(f"data/{st.session_state['username']}/health_data.csv", index=False)  # Save updated DataFrame to CSV
        st.success("New data added!")
        st.rerun()  # Rerun the app to reflect the change
    except ValueError:
        st.error(f"Invalid value(s): {new_value}. Please enter valid number(s).")
    