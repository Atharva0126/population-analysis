import streamlit as st
import pandas as pd

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Population Data Analysis",
    layout="wide"
)

# Load CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Singapore_Residents_edit.csv")

df = load_data()

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 Analysis Options")

task = st.sidebar.selectbox(
    "Select Task",
    (
        "View Raw Data",
        "Total Population Every Year",
        "Male–Female Ratio (Every 3 Years)",
        "Population Growth Percentage"
    )
)

# ---------------- MAIN UI ----------------
st.title("📈 Singapore Population Analysis")

# ---------------- TASK 0 ----------------
if task == "View Raw Data":
    st.subheader("Raw Dataset")
    st.dataframe(df, use_container_width=True)

# ---------------- TASK 1 ----------------
elif task == "Total Population Every Year":
    st.subheader("Total Population Every Year")

    total_pop = df[df["Residents"] == "Total Residents"]
    result = (
        total_pop
        .groupby("Year")["Count"]
        .sum()
        .reset_index()
    )

    st.dataframe(result, use_container_width=True)

# ---------------- TASK 2 ----------------
elif task == "Male–Female Ratio (Every 3 Years)":
    st.subheader("Male–Female Ratio (Every 3 Years)")

    male_df = df[df["Residents"].str.contains("Male", case=False)]
    female_df = df[df["Residents"].str.contains("Female", case=False)]

    male_df["Category"] = male_df["Residents"].str.replace("Male", "", case=False)
    female_df["Category"] = female_df["Residents"].str.replace("Female", "", case=False)

    male_count = (
        male_df
        .groupby(["Category", "Year_Group"])["Count"]
        .sum()
        .reset_index(name="Male")
    )

    female_count = (
        female_df
        .groupby(["Category", "Year_Group"])["Count"]
        .sum()
        .reset_index(name="Female")
    )

    gender_ratio = pd.merge(
        male_count,
        female_count,
        on=["Category", "Year_Group"],
        how="inner"
    )

    gender_ratio["Female_to_Male_Ratio"] = (
        gender_ratio["Female"] / gender_ratio["Male"]
    ).round(2)

    st.dataframe(gender_ratio, use_container_width=True)

# ---------------- TASK 3 ----------------
elif task == "Population Growth Percentage":
    st.subheader("Population Growth Percentage")

    total_pop = df[df["Residents"] == "Total Residents"]
    total_pop = total_pop.sort_values("Year")

    total_pop["Population_Growth_%"] = (
        total_pop["Count"].pct_change() * 100
    ).round(2)

    result = total_pop[["Year", "Count", "Population_Growth_%"]]

    st.dataframe(result, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<center>📌 Beginner-Friendly Pandas + Streamlit Project</center>",
    unsafe_allow_html=True
)

