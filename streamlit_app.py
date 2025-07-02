import altair as alt
import pandas as pd
import streamlit as st

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
    df = pd.read_csv("data/health_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])  # Convert 'date' column to datetime
    return df

df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
types = st.multiselect(
    "Types",
    df.Type.unique(),
    ["Weight", "BMI", "Cholesterol", "Triglycerides", "HDL", "LDL", "TC-HDL", "TC/HDL"], # Default selection
)

col1, col2 = st.columns(2)
with col1: start_date = st.date_input("Start date", df["Date"].min())
with col2: end_date = st.date_input("End date", df["Date"].max())

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    (df["Type"].isin(types)) &
    (df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date)))
]
df_reshaped = df_filtered.pivot_table(
    index="Date", columns="Type", values="Value", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="Date", ascending=False)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="Date", var_name="Type", value_name="Value"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("Date:T"), # axis=alt.Axis(format="%Y-%m-%d")
        y=alt.Y("Value:Q"),
        #color="Type:N",
        color=alt.Color("Type:N", legend=alt.Legend(orient="bottom")),  # Legend at bottom
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
if "Ketones" in df_display.columns: desired_order += ["Ketones"]
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
    "Glucose Ketones",
    "Glucose",
    "Ketones",
]

with st.form("Add new record"):
    new_date = st.date_input("Date")
    new_type = st.selectbox("Type", record_types)
    new_value = st.text_input("Value(s)")  # String input
    new_note = st.text_input("Note (optional)")  # String input
    submitted = st.form_submit_button("Add")

if submitted:
    try:
        values = new_value.split(" ")
        new_date = pd.to_datetime(new_date)
        if new_type == "Weight":
            weight = { "Date": new_date, "Type": "Weight", "Value": float(values[0]), "Note": new_note }
            # BMI = weight in lbs x 703 / (height in inches)^2
            bmi = { "Date": new_date, "Type": "BMI", "Value": float(values[0])*703 / (5*12+6)**2, "Note": new_note }
            df = pd.concat([df, pd.DataFrame([weight, bmi])], ignore_index=True)
        elif new_type == "Cholesterol Triglycerides HDL LDL":
            cholesterol = { "Date": new_date, "Type": "Cholesterol", "Value": float(values[0]), "Note": new_note }
            triglycerides = { "Date": new_date, "Type": "Triglycerides", "Value": float(values[1]), "Note": new_note }
            hdl = { "Date": new_date, "Type": "HDL", "Value": float(values[2]), "Note": new_note }
            ldl = { "Date": new_date, "Type": "LDL", "Value": float(values[3]), "Note": new_note }
            tc_hdl = { "Date": new_date, "Type": "TC-HDL", "Value": float(values[0])-float(values[2]), "Note": new_note }
            tc_hdl_ratio = { "Date": new_date, "Type": "TC/HDL", "Value": float(values[0])/float(values[2]), "Note": new_note }
            df = pd.concat([df, pd.DataFrame([cholesterol, triglycerides, hdl, ldl, tc_hdl, tc_hdl_ratio])], ignore_index=True)
        elif new_type == "Glucose Ketones":
            glucose = { "Date": new_date, "Type": "Glucose", "Value": float(values[0]), "Note": new_note }
            ketones = { "Date": new_date, "Type": "Ketones", "Value": float(values[1]), "Note": new_note }
            df = pd.concat([df, pd.DataFrame([glucose, ketones])], ignore_index=True)
        else:
            value = { "Date": new_date, "Type": new_type, "Value": float(values[0]), "Note": new_note }
            df = pd.concat([df, pd.DataFrame([value])], ignore_index=True)
    except ValueError:
        st.error(f"Invalid value(s): {new_value}. Please enter valid number(s).")
    df.to_csv("data/health_data.csv", index=False)  # Save updated DataFrame to CSV
    st.success("New data added!")
    