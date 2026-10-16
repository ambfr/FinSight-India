
import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("market_data.csv", parse_dates=["Date"])
    return df.dropna(subset=["Date", "Close"]).sort_values("Date")

df = load_data()

st.title("🏭 Sector Analysis")
st.caption("Compare the historical performance of Indian market sectors.")

sector_mapping = {
    "HDFC Bank": "Banking",
    "ICICI Bank": "Banking",
    "State Bank of India": "Banking",
    "TCS": "IT",
    "Infosys": "IT",
    "Reliance Industries": "Energy",
    "ONGC": "Energy",
    "ITC": "Consumer Goods",
    "Hindustan Unilever": "Consumer Goods",
    "Mahindra & Mahindra": "Automotive"
}

df["Sector"] = df["Company"].map(sector_mapping)
df = df.dropna(subset=["Sector"])

sectors = sorted(df["Sector"].unique())
selected_sectors = st.multiselect(
    "Select sectors",
    sectors,
    default=sectors
)

if not selected_sectors:
    st.info("Select at least one sector.")
    st.stop()

data = df[df["Sector"].isin(selected_sectors)].copy()

company_returns = []

for company, group in data.groupby("Company"):
    group = group.sort_values("Date")
    prices = group["Close"].dropna()

    if len(prices) >= 2:
        company_returns.append({
            "Company": company,
            "Sector": group["Sector"].iloc[0],
            "Latest Price (₹)": prices.iloc[-1],
            "Period Return (%)": (
                prices.iloc[-1] / prices.iloc[0] - 1
            ) * 100
        })

returns_df = pd.DataFrame(company_returns)

if not returns_df.empty:
    sector_summary = (
        returns_df.groupby("Sector")["Period Return (%)"]
        .mean()
        .reset_index()
        .rename(columns={
            "Period Return (%)": "Average Company Return (%)"
        })
    )

    st.subheader("Average Company Return by Sector")
    fig = px.bar(
        sector_summary,
        x="Sector",
        y="Average Company Return (%)",
        color="Sector",
        template="plotly_dark",
        title="Average return of companies within each sector"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sector Performance Over Time")

    data["Indexed Price"] = (
        data["Close"]
        / data.groupby("Company")["Close"].transform("first")
        * 100
    )

    sector_trends = (
        data.groupby(["Date", "Sector"])["Indexed Price"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        sector_trends,
        x="Date",
        y="Indexed Price",
        color="Sector",
        template="plotly_dark",
        title="Average indexed price (base = 100)"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Company-Level Performance")
    st.dataframe(
        returns_df.round(2),
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Sector results are based on the selected companies in this dataset, "
    "not every company in the sector."
)
