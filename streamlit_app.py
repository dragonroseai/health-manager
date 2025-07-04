import altair as alt
import datetime as dt
import pandas as pd
import streamlit as st

# --- Simple authentication setup ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if st.session_state["authenticated"]:
        return True

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
                print(st.session_state)
                st.rerun()
            else:
                st.error("Invalid username or password.")
    return False

if not check_password():
    st.stop()
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
    index="Date", columns="Name", values="Value", aggfunc="sum", fill_value=0
)
selected = []
if "Weight" in df_pivot.columns: selected += ["Weight"]
# if "BMI" in df_pivot.columns: selected += ["BMI"]
if "Cholesterol" in df_pivot.columns: selected += ["Cholesterol"]
if "Triglycerides" in df_pivot.columns: selected += ["Triglycerides"]
if "HDL" in df_pivot.columns: selected += ["HDL"]
if "LDL" in df_pivot.columns: selected += ["LDL"]
# if "TC-HDL" in df_pivot.columns: selected += ["TC-HDL"]
# if "TC/HDL" in df_pivot.columns: selected += ["TC/HDL"]
if "Glucose" in df_pivot.columns: selected += ["Glucose"]
# if "Ketone" in df_pivot.columns: selected += ["Ketone"]
# selected = ["Cholesterol"]  # Default selected for demo purposes
names = st.multiselect("Measurements", df.Name.unique(), selected)

col1, col2 = st.columns(2)
with col1: 
    #start_date = st.date_input("Start date", dt.date(2024,11,1))  # Default start date for demo purposes
    #start_date = st.date_input("Start date", df["Date"].min())
    start_date = st.date_input("Start date", df["Date"].max() - pd.DateOffset(years=1))
with col2: 
    end_date = st.date_input("End date", df["Date"].max())

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    (df["Name"].isin(names)) &
    (df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)))
]
df_reshaped = df_filtered.pivot_table(
    index="Date", columns="Name", values="Value", aggfunc="sum", fill_value=0
)
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
        color=alt.Color("Name:N", legend=alt.Legend(orient="bottom")),  # Legend at bottom
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

# Display the data as a table using `st.dataframe`.
df_display = df_reshaped.copy()
df_display.index = df_display.index.strftime("%Y-%m-%d")  # Format index if 'date' is index
df_display = df_display.reset_index()
for col in df_display.columns:
    if col != "Date":
        df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
desired_order = ["Date"]
if "Weight" in df_display.columns: desired_order += ["Weight"]
if "BMI" in df_display.columns: desired_order += ["BMI"]
if "Cholesterol" in df_display.columns: desired_order += ["Cholesterol"]
if "Triglycerides" in df_display.columns: desired_order += ["Triglycerides"]
if "HDL" in df_display.columns: desired_order += ["HDL"]
if "LDL" in df_display.columns: desired_order += ["LDL"]
if "TC-HDL" in df_display.columns: desired_order += ["TC-HDL"]
if "TC/HDL" in df_display.columns: desired_order += ["TC/HDL"]
if "Glucose" in df_display.columns: desired_order += ["Glucose"]
if "Ketone" in df_display.columns: desired_order += ["Ketone"]
for col in df_display.columns:
    if col not in desired_order:
        desired_order.append(col)  # Append any other columns that are not in the desired order
st.dataframe(
    df_display[desired_order],
    use_container_width=True,
    hide_index=True,  # Hide the index column
)

record_types = [
    "Weight",
    "Cholesterol Triglycerides HDL LDL",
    "Cholesterol",
    "Triglycerides",
    "HDL",
    "LDL",
    "Glucose Ketone",
    "Glucose",
    "Ketone",
]

with st.form("Add new record"):
    new_date = st.date_input("Date")
    new_type = st.selectbox("Name", record_types)
    new_value = st.text_input("Value(s)")  # String input
    new_note = st.text_input("Note (optional)")  # String input
    submitted = st.form_submit_button("Add")

if submitted:
    try:
        values = new_value.split(" ")
        new_date = pd.to_datetime(new_date)
        if new_type == "Weight":
            weight = { "Date": new_date, "Name": "Weight", "Value": float(values[0]), "Note": new_note }
            # BMI = weight in lbs x 703 / (height in inches)^2
            bmi = { "Date": new_date, "Name": "BMI", "Value": float(values[0])*703 / (5*12+6)**2, "Note": new_note }
            df = pd.concat([df, pd.DataFrame([weight, bmi])], ignore_index=True)
        elif new_type == "Cholesterol Triglycerides HDL LDL":
            cholesterol = { "Date": new_date, "Name": "Cholesterol", "Value": float(values[0]), "Note": new_note }
            triglycerides = { "Date": new_date, "Name": "Triglycerides", "Value": float(values[1]), "Note": new_note }
            hdl = { "Date": new_date, "Name": "HDL", "Value": float(values[2]), "Note": new_note }
            ldl = { "Date": new_date, "Name": "LDL", "Value": float(values[3]), "Note": new_note }
            tc_hdl = { "Date": new_date, "Name": "TC-HDL", "Value": float(values[0])-float(values[2]), "Note": new_note }
            tc_hdl_ratio = { "Date": new_date, "Name": "TC/HDL", "Value": float(values[0])/float(values[2]), "Note": new_note }
            df = pd.concat([df, pd.DataFrame([cholesterol, triglycerides, hdl, ldl, tc_hdl, tc_hdl_ratio])], ignore_index=True)
        elif new_type == "Glucose Ketone":
            glucose = { "Date": new_date, "Name": "Glucose", "Value": float(values[0]), "Note": new_note }
            ketone = { "Date": new_date, "Name": "Ketone", "Value": float(values[1]), "Note": new_note }
            df = pd.concat([df, pd.DataFrame([glucose, ketone])], ignore_index=True)
        else:
            value = { "Date": new_date, "Name": new_type, "Value": float(values[0]), "Note": new_note }
            df = pd.concat([df, pd.DataFrame([value])], ignore_index=True)
    except ValueError:
        st.error(f"Invalid value(s): {new_value}. Please enter valid number(s).")
    df.to_csv(f"data/{st.session_state['username']}/health_data.csv", index=False)  # Save updated DataFrame to CSV
    st.success("New data added!")
    