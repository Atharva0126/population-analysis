import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Population Data Analysis", layout="wide")

# ---------------- LOAD CSS ----------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Singapore_Residents_edit.csv")

df = load_data()

# ---------------- CREATE YEAR GROUP ----------------
df["Year_Group"] = (df["Year"] // 3) * 3

# ==================================================
# GLOBAL FILTERS (SIDEBAR)
# ==================================================
st.sidebar.title("🔎 Global Filters")

# Category filter (derived from Residents)
df["Category"] = (
    df["Residents"]
    .str.replace("Male", "", case=False)
    .str.replace("Female", "", case=False)
)

category_list = sorted(df["Category"].dropna().unique())
selected_category = st.sidebar.selectbox(
    "Select Category",
    ["All"] + category_list
)

# Year Group filter
year_groups = sorted(df["Year_Group"].unique())
selected_year_groups = st.sidebar.multiselect(
    "Select Year Group (3-Year Window)",
    year_groups,
    default=year_groups
)

# Apply filters ONCE
df_filtered = df.copy()

if selected_category != "All":
    df_filtered = df_filtered[df_filtered["Category"] == selected_category]

df_filtered = df_filtered[
    df_filtered["Year_Group"].isin(selected_year_groups)
]

# ==================================================
# TASK SELECTION
# ==================================================
st.sidebar.title("📊 Analysis Tasks")

task = st.sidebar.selectbox(
    "Select Task",
    (
        "View Raw Data",
        "Total Population Every Year",
        "Male–Female Ratio (Every 3 Years)",
        "Population Growth Percentage"
    )
)

# ---------------- MAIN TITLE ----------------
st.title("📈 Singapore Population Analysis")

# ==================================================
# TASK 0 : VIEW RAW DATA
# ==================================================
if task == "View Raw Data":
    st.subheader("Raw Dataset (Filtered)")
    st.dataframe(df_filtered, use_container_width=True)

# ==================================================
# TASK 1 : TOTAL POPULATION EVERY YEAR
# ==================================================
elif task == "Total Population Every Year":
    st.subheader("Total Population Every Year")

    total_pop = df_filtered[df_filtered["Residents"] == "Total Residents"]

    result = (
        total_pop
        .groupby("Year")["Count"]
        .sum()
        .reset_index()
    )

    st.dataframe(result, use_container_width=True)

# ==================================================
# TASK 2 : MALE–FEMALE RATIO
# ==================================================
elif task == "Male–Female Ratio (Every 3 Years)":
    st.subheader("Male–Female Ratio (Every 3 Years)")

    male_df = df_filtered[df_filtered["Residents"].str.contains("Male", case=False, na=False)]
    female_df = df_filtered[df_filtered["Residents"].str.contains("Female", case=False, na=False)]

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

# ==================================================
# TASK 3 : POPULATION GROWTH
# ==================================================
elif task == "Population Growth Percentage":
    st.subheader("Population Growth Percentage")

    total_pop = df_filtered[df_filtered["Residents"] == "Total Residents"]
    total_pop = total_pop.sort_values("Year")

    total_pop["Population_Growth_%"] = (
        total_pop["Count"].pct_change() * 100
    ).round(2)

    result = total_pop[["Year", "Count", "Population_Growth_%"]]

    st.dataframe(result, use_container_width=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown(
    "<center>Global Filters persist across all tasks</center>",
    unsafe_allow_html=True
)
