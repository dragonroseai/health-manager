import altair as alt
import auth
import home
import new_entry
import os
import pandas as pd
import settings
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Health Manager", page_icon="❤️", layout="wide")
st.title("Health Manager ❤️")

if not auth.check_password(): st.stop()
#st.session_state["email"] = "hiangswee"  # Default email for demo purposes

# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
#@st.cache_data
def load_data():
    df = pd.read_csv(f"data/{st.session_state['email']}/health_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])  # Convert 'date' column to datetime
    return df

df = load_data()

page = st.sidebar.radio(
    "Menu",
    ("Home", "New Entry", "Settings"),
    index=0
)

if page == "New Entry":
    settings_file = f"data/{st.session_state["email"]}/settings.json"
    if not os.path.exists(settings_file):
        st.info("Please set your height before adding new entries.")
        settings.show()
    else:
        new_entry.show(df)
    st.stop()  # Stop here so the rest of the app doesn't run
elif page == "Settings":
    settings.show()
    st.stop()  # Stop here so the rest of the app doesn't run

if st.session_state.get("rerun", False) == True:
    st.session_state["rerun"] = False  # Reset rerun flag
    st.rerun()

names = home.show_measurement_selection(df)

start_date, end_date, show_ma = home.show_date_selection(df)

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    (df["Name"].isin(names)) &
    (df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date+pd.DateOffset(days=1))))
]

# Display the data as an Altair chart using `st.altair_chart`.
df_reshaped = df_filtered.pivot_table(index="Date", columns="Name", values="Value", aggfunc="mean")
df_reshaped = df_reshaped.sort_index().ffill()
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
# Calculate 1-month (30-day) moving average for each measurement
df_ma = df_reshaped.rolling(window='30D', min_periods=1).mean()
df_ma_chart = pd.melt(
    df_ma.reset_index(), id_vars="Date", var_name="Name", value_name="Value"
)
ma_chart = (
    alt.Chart(df_ma_chart)
    .mark_line(strokeDash=[5,5], opacity=0.7)
    .encode(
        x=alt.X("Date:T"),
        y=alt.Y("Value:Q"),
        color=alt.Color("Name:N", legend=None),
    )
)
if show_ma:
    st.altair_chart(chart + ma_chart, use_container_width=True)
else:
    st.altair_chart(chart, use_container_width=True)

# Display the data as a table using `st.dataframe`.
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
df_reshaped = df_reshaped.sort_values(by="Date", ascending=False)
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
    