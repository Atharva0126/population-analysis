import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Population Data Analysis",
    layout="wide"
)

# ---------------- LOAD CSS ----------------
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("data/Singapore_Residents_edit.csv")

df = load_data()

# ---------------- CREATE YEAR GROUP (3 YEARS) ----------------
df["Year_Group"] = (df["Year"] // 3) * 3

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

# ---------------- MAIN TITLE ----------------
st.title("📈 Singapore Population Analysis")

# ==========================================================
# TASK 0 : VIEW RAW DATA
# ==========================================================
if task == "View Raw Data":
    st.subheader("Raw Dataset")
    st.dataframe(df, use_container_width=True)

# ==========================================================
# TASK 1 : TOTAL POPULATION EVERY YEAR
# ==========================================================
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

# ==========================================================
# TASK 2 : MALE–FEMALE RATIO (WITH FILTERS & SORTING)
# ==========================================================
elif task == "Male–Female Ratio (Every 3 Years)":
    st.subheader("Male–Female Ratio (Every 3 Years)")

    # ---- Separate Male & Female ----
    male_df = df[df["Residents"].str.contains("Male", case=False, na=False)]
    female_df = df[df["Residents"].str.contains("Female", case=False, na=False)]

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

    # ---------------- FILTERS ----------------
    st.subheader("Filters & Sorting")

    # Category Filter
    category_list = sorted(gender_ratio["Category"].unique())
    selected_category = st.selectbox(
        "Select Category",
        ["All"] + category_list
    )

    if selected_category != "All":
        gender_ratio = gender_ratio[
            gender_ratio["Category"] == selected_category
        ]

    # Year Group Filter
    year_groups = sorted(gender_ratio["Year_Group"].unique())
    selected_years = st.multiselect(
        "Select Year Group (3-Year Window)",
        year_groups,
        default=year_groups
    )

    gender_ratio = gender_ratio[
        gender_ratio["Year_Group"].isin(selected_years)
    ]

    # Sorting
    sort_column = st.selectbox(
        "Sort By",
        ["Year_Group", "Female_to_Male_Ratio", "Female", "Male"]
    )

    sort_order = st.radio(
        "Sort Order",
        ["Ascending", "Descending"],
        horizontal=True
    )

    gender_ratio = gender_ratio.sort_values(
        by=sort_column,
        ascending=(sort_order == "Ascending")
    )

    # ---------------- DISPLAY ----------------
    st.dataframe(gender_ratio, use_container_width=True)

# ==========================================================
# TASK 3 : POPULATION GROWTH
# ==========================================================
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
    "<center>Beginner-Friendly Pandas + Streamlit Project</center>",
    unsafe_allow_html=True
)
