import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Health Manager", page_icon="🎬")
st.title("🎬 Health Manager")
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
    df["date"] = pd.to_datetime(df["date"])  # Convert 'date' column to datetime
    return df

df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
types = st.multiselect(
    "Types",
    df.type.unique(),
    ["Weight", "BMI", "Cholesterol", "Triglycerides", "HDL", "LDL", "TC-HDL", "TC/HDL"], # Default selection
)

date_range = st.date_input("Date range", [df["date"].min(), df["date"].max()])

# Filter the dataframe based on the widget input and reshape it.
df_filtered = df[
    (df["type"].isin(types)) &
    (df["date"].between(pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])))
]
df_reshaped = df_filtered.pivot_table(
    index="date", columns="type", values="value", aggfunc="sum", fill_value=0
)
df_reshaped = df_reshaped.sort_values(by="date", ascending=False)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="date", var_name="type", value_name="value"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("date:T", title="Date"), # axis=alt.Axis(format="%Y-%m-%d")
        y=alt.Y("value:Q", title="mg/dL"),
        color="type:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)

# Display the data as a table using `st.dataframe`.
df_display = df_reshaped.copy()
df_display.index = df_display.index.strftime("%Y-%m-%d")  # Format index if 'date' is index
df_display = df_display.reset_index()
for col in df_display.columns:
    if col != "date":
        df_display[col] = df_display[col].apply(lambda x: f"{x:.1f}" if pd.notnull(x) else "")
desired_order = ["date"]
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

with st.form("Add new record"):
    new_date = st.date_input("Date")
    new_type = st.selectbox("Type", ["Weight", "Cholesterol Triglycerides HDL LDL", "Cholesterol", "Glucose Ketones", "Glucose"])
    new_value = st.text_input("Value(s)")  # String input
    new_note = st.text_input("Note (optional)")  # String input
    submitted = st.form_submit_button("Add")

if submitted:
    try:
        values = new_value.split(" ")
        new_date = pd.to_datetime(new_date)
        if new_type == "Weight":
            weight = { "date": new_date, "type": "Weight", "value": float(values[0]) }
            # BMI = weight in lbs x 703 / (height in inches)^2
            bmi = { "date": new_date, "type": "BMI", "value": float(values[0])*703 / (5*12+6)**2 }
            df = pd.concat([df, pd.DataFrame([weight, bmi])], ignore_index=True)
        elif new_type == "Cholesterol Triglycerides HDL LDL":
            cholesterol = { "date": new_date, "type": "Cholesterol", "value": float(values[0]) }
            triglycerides = { "date": new_date, "type": "Triglycerides", "value": float(values[1]) }
            hdl = { "date": new_date, "type": "HDL", "value": float(values[2]) }
            ldl = { "date": new_date, "type": "LDL", "value": float(values[3]) }
            tc_hdl = { "date": new_date, "type": "TC-HDL", "value": float(values[0])-float(values[2]) }
            tc_hdl_ratio = { "date": new_date, "type": "TC/HDL", "value": float(values[0])/float(values[2]) }
            df = pd.concat([df, pd.DataFrame([cholesterol, triglycerides, hdl, ldl, tc_hdl, tc_hdl_ratio])], ignore_index=True)
        elif new_type == "Glucose Ketones":
            glucose = { "date": new_date, "type": "Glucose", "value": float(values[0]) }
            ketones = { "date": new_date, "type": "Ketones", "value": float(values[1]) }
            df = pd.concat([df, pd.DataFrame([glucose, ketones])], ignore_index=True)
        elif new_type == "Cholesterol":
            cholesterol = { "date": new_date, "type": "Cholesterol", "value": float(values[0]) }
            df = pd.concat([df, pd.DataFrame([cholesterol])], ignore_index=True)
        elif new_type == "Glucose":
            glucose = { "date": new_date, "type": "Glucose", "value": float(values[0]) }
            df = pd.concat([df, pd.DataFrame([glucose])], ignore_index=True)
    except ValueError:
        st.error(f"Invalid value(s): {new_value}. Please enter valid number(s).")
    df.to_csv("data/health_data.csv", index=False)  # Save updated DataFrame to CSV
    st.success("New data added!")
    