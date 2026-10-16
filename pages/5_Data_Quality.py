
import streamlit as st
import pandas as pd
from datetime import date

st.title("🔎 Data Quality")
st.caption("Monitor the reliability and completeness of FinSight India data.")

@st.cache_data
def load_data():
    return pd.read_csv("market_data.csv", parse_dates=["Date"])

try:
    df = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Unable to load market_data.csv: {error}")
    st.stop()

required_columns = {"Date", "Company", "Close"}
missing_columns = required_columns - set(df.columns)

if missing_columns:
    st.error(f"Required columns missing: {sorted(missing_columns)}")
    st.stop()

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Close"] = pd.to_numeric(df["Close"], errors="coerce")

duplicate_count = int(
    df.duplicated(["Date", "Company"]).sum()
)

missing_dates = int(df["Date"].isna().sum())
missing_companies = int(df["Company"].isna().sum())
missing_prices = int(df["Close"].isna().sum())

invalid_prices = int(
    (df["Close"].notna() & (df["Close"] <= 0)).sum()
)

latest_date = df["Date"].max()

if pd.notna(latest_date):
    days_old = (pd.Timestamp(date.today()) - latest_date.normalize()).days
else:
    days_old = None

c1, c2, c3 = st.columns(3)
c1.metric("Total Records", f"{len(df):,}")
c2.metric("Companies", df["Company"].nunique())
c3.metric("Duplicate Records", duplicate_count)

st.subheader("Completeness Checks")

quality_summary = pd.DataFrame({
    "Check": [
        "Missing dates",
        "Missing company names",
        "Missing closing prices",
        "Non-positive closing prices",
        "Duplicate date/company records"
    ],
    "Issues Found": [
        missing_dates,
        missing_companies,
        missing_prices,
        invalid_prices,
        duplicate_count
    ]
})

st.dataframe(
    quality_summary,
    use_container_width=True,
    hide_index=True
)

if (
    missing_dates == 0
    and missing_companies == 0
    and missing_prices == 0
    and invalid_prices == 0
    and duplicate_count == 0
):
    st.success("No issues found in the selected quality checks.")
else:
    st.warning("Some data quality issues need investigation.")

st.subheader("Data Freshness")

if days_old is not None:
    c1, c2 = st.columns(2)
    c1.metric("Latest Data Date", latest_date.strftime("%d %b %Y"))
    c2.metric("Calendar Days Since Latest Record", days_old)

    if days_old <= 4:
        st.success("The latest record is recent by calendar date.")
    else:
        st.warning(
            "The latest record may be stale. Check the exchange calendar "
            "and refresh the data before drawing conclusions."
        )
else:
    st.error("No valid dates were found.")

st.subheader("Company Coverage")

coverage = (
    df.groupby("Company")
    .agg(
        Records=("Close", "size"),
        First_Date=("Date", "min"),
        Latest_Date=("Date", "max"),
        Missing_Prices=("Close", lambda s: int(s.isna().sum()))
    )
    .reset_index()
)

st.dataframe(
    coverage,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Freshness is measured in calendar days, not trading days. "
    "A warning alone does not prove that data is incorrect."
)
