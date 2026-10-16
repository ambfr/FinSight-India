
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("market_data.csv", parse_dates=["Date"])
    return df.sort_values(["Date", "Company"])

df = load_data()

st.title("🗂️ Data Explorer")
st.caption("Explore, filter and export the historical stock dataset.")

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", f"{len(df):,}")
c2.metric("Companies", df["Company"].nunique())
c3.metric("Date Range (days)", (df["Date"].max() - df["Date"].min()).days)

st.divider()

companies = sorted(df["Company"].dropna().unique())

selected = st.multiselect(
    "Filter by company",
    companies,
    default=companies
)

min_date = df["Date"].min().date()
max_date = df["Date"].max().date()

date_range = st.date_input(
    "Select date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if not selected:
    st.info("Select at least one company.")
    st.stop()

filtered = df[df["Company"].isin(selected)].copy()

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["Date"].dt.date >= start_date)
        & (filtered["Date"].dt.date <= end_date)
    ]

st.subheader("Filtered Dataset")
st.write(f"Showing **{len(filtered):,}** records.")

st.dataframe(
    filtered,
    use_container_width=True,
    hide_index=True
)

st.download_button(
    label="⬇️ Download Filtered CSV",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="finsight_filtered_data.csv",
    mime="text/csv"
)

st.divider()
st.subheader("Dataset Information")

info = pd.DataFrame({
    "Column": df.columns,
    "Data Type": [str(dtype) for dtype in df.dtypes],
    "Missing Values": [int(value) for value in df.isna().sum()]
})

st.dataframe(info, use_container_width=True, hide_index=True)
