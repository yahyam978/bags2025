import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Bag Model Color Analysis",
    page_icon="🎒",
    layout="wide"
)

st.title("🎒 Bag Model Color Summary Dashboard")

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    raw_df = pd.read_csv("processed_sales_summary.csv")

    # First row contains model + color info
    header_row = raw_df.iloc[0]
    data_df = raw_df.iloc[1:].copy()

    # Rename columns using header row
    data_df.columns = header_row
    data_df.rename(columns={data_df.columns[0]: "Month"}, inplace=True)

    # Drop empty columns
    data_df = data_df.dropna(axis=1, how="all")

    # Melt to long format
    melted = data_df.melt(
        id_vars="Month",
        var_name="Model_Color",
        value_name="Quantity"
    )

    # Clean data
    melted["Quantity"] = pd.to_numeric(melted["Quantity"], errors="coerce").fillna(0)

    # Split Model and Color
    melted["Model"] = melted["Model_Color"].str.split().str[0]
    melted["Color"] = melted["Model_Color"].str.replace(melted["Model"] + " ", "", regex=True)

    return melted

df = load_data()

# -----------------------------
# Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

models = sorted(df["Model"].unique())
selected_model = st.sidebar.selectbox("Select Model", models)

# -----------------------------
# Filter Data
# -----------------------------
model_df = df[df["Model"] == selected_model]

color_summary = (
    model_df.groupby("Color", as_index=False)["Quantity"]
    .sum()
    .sort_values(by="Quantity", ascending=False)
)

total_quantity = int(color_summary["Quantity"].sum())

# -----------------------------
# KPI Section
# -----------------------------
col1, col2 = st.columns(2)

col1.metric(
    label=f"Total Quantity for Model {selected_model}",
    value=f"{total_quantity:,}"
)

col2.metric(
    label="Number of Colors",
    value=color_summary.shape[0]
)

# -----------------------------
# Table
# -----------------------------
st.subheader("📊 Quantity per Color")
st.dataframe(
    color_summary,
    use_container_width=True
)

# -----------------------------
# Chart
# -----------------------------
st.subheader("🎨 Color Distribution")

fig = px.bar(
    color_summary,
    x="Color",
    y="Quantity",
    text="Quantity",
)

fig.update_layout(
    xaxis_title="Color",
    yaxis_title="Quantity",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Download Option
# -----------------------------
st.subheader("⬇️ Download Data")

csv = color_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Color Summary as CSV",
    data=csv,
    file_name=f"{selected_model}_color_summary.csv",
    mime="text/csv"
)
