import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Bag Model Color Summary Dashboard",
    page_icon="🎒",
    layout="wide"
)

st.title("🎒 Bag Model Color Summary Dashboard")

@st.cache_data
def load_data():
    raw_df = pd.read_csv("processed_sales_summary.csv")

    # First row contains headers
    header_row = raw_df.iloc[0]
    data_df = raw_df.iloc[1:].copy()

    data_df.columns = header_row
    data_df.rename(columns={data_df.columns[0]: "Month"}, inplace=True)
    data_df = data_df.dropna(axis=1, how="all")

    melted = data_df.melt(
        id_vars="Month",
        var_name="Model_Color",
        value_name="Quantity"
    )

    melted["Quantity"] = pd.to_numeric(
        melted["Quantity"], errors="coerce"
    ).fillna(0)

    # SAFE split
    split_data = melted["Model_Color"].astype(str).str.split(" ", n=1, expand=True)
    melted["Model"] = split_data[0]
    melted["Color"] = split_data[1]

    melted = melted.dropna(subset=["Color"])

    return melted


df = load_data()

st.sidebar.header("🔍 Filters")
models = sorted(df["Model"].unique())
selected_model = st.sidebar.selectbox("Select Model", models)

model_df = df[df["Model"] == selected_model]

color_summary = (
    model_df
    .groupby("Color", as_index=False)["Quantity"]
    .sum()
    .sort_values(by="Quantity", ascending=False)
)

total_quantity = int(color_summary["Quantity"].sum())

col1, col2 = st.columns(2)
col1.metric("Total Quantity", f"{total_quantity:,}")
col2.metric("Number of Colors", color_summary.shape[0])

st.subheader("📊 Quantity per Color")
st.dataframe(color_summary, use_container_width=True)

st.subheader("🎨 Color Distribution")
fig = px.bar(color_summary, x="Color", y="Quantity", text_auto=True)
st.plotly_chart(fig, use_container_width=True)

csv = color_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download CSV",
    csv,
    f"{selected_model}_color_summary.csv",
    "text/csv"
)
