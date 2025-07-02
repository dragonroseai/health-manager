import altair as alt
import pandas as pd
import streamlit as st

# Show the page title and description.
st.set_page_config(page_title="Cholesterol Manager", page_icon="🎬")
st.title("🎬 Cholesterol Manager")
st.write(
    """
    This app visualizes your cholesterol data. Just 
    click on the widgets below to explore!
    """
)


# Load the data from a CSV. We're caching this so it doesn't reload every time the app
# reruns (e.g. if the user interacts with the widgets).
@st.cache_data
def load_data():
    df = pd.read_csv("data/cholesterol.csv")
    df["date"] = pd.to_datetime(df["date"])  # Convert 'date' column to datetime
    return df

df = load_data()

# Show a multiselect widget with the genres using `st.multiselect`.
types = st.multiselect(
    "Types",
    df.type.unique(),
    ["Total Cholesterol", "Triglycerides"],
)

print(df["date"].min(), df["date"].max())
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


# Display the data as a table using `st.dataframe`.
st.dataframe(
    df_reshaped,
    use_container_width=True,
)

# Display the data as an Altair chart using `st.altair_chart`.
df_chart = pd.melt(
    df_reshaped.reset_index(), id_vars="date", var_name="type", value_name="value"
)
chart = (
    alt.Chart(df_chart)
    .mark_line()
    .encode(
        x=alt.X("date:T", title="Date"),
        y=alt.Y("value:Q", title="mg/dL"),
        color="type:N",
    )
    .properties(height=320)
)
st.altair_chart(chart, use_container_width=True)
