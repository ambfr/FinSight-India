
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

@st.cache_data
def load_data():
    df = pd.read_csv("market_data.csv", parse_dates=["Date"])
    return df.dropna(subset=["Date", "Close"]).sort_values("Date")

df = load_data()

st.title("📉 Risk & Correlation")
st.caption("Understand historical stock risk and relationships.")

companies = sorted(df["Company"].unique())
selected = st.multiselect(
    "Select companies",
    companies,
    default=companies
)

if not selected:
    st.info("Select at least one company.")
    st.stop()

data = df[df["Company"].isin(selected)].copy()
data = data.sort_values(["Company", "Date"])

data["Daily Return (%)"] = (
    data.groupby("Company")["Close"].pct_change() * 100
)

risk_rows = []

for company, group in data.groupby("Company"):
    group = group.sort_values("Date")
    prices = group["Close"].dropna()
    daily_returns = prices.pct_change().dropna()

    if len(prices) < 2:
        continue

    running_peak = prices.cummax()
    drawdown = (prices / running_peak - 1) * 100

    risk_rows.append({
        "Company": company,
        "Latest Price (₹)": prices.iloc[-1],
        "Annualized Volatility (%)":
            daily_returns.std() * np.sqrt(252) * 100,
        "Maximum Drawdown (%)": drawdown.min()
    })

risk_df = pd.DataFrame(risk_rows)

st.subheader("Historical Risk Metrics")

if not risk_df.empty:
    c1, c2 = st.columns(2)
    c1.metric("Companies Analysed", len(risk_df))
    c2.metric(
        "Highest Volatility",
        risk_df.loc[
            risk_df["Annualized Volatility (%)"].idxmax(),
            "Company"
        ]
    )

    fig = px.bar(
        risk_df,
        x="Company",
        y="Annualized Volatility (%)",
        color="Company",
        template="plotly_dark",
        title="Annualized Historical Volatility"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        risk_df,
        x="Company",
        y="Maximum Drawdown (%)",
        color="Company",
        template="plotly_dark",
        title="Maximum Historical Drawdown"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        risk_df.round(2),
        use_container_width=True,
        hide_index=True
    )

st.divider()
st.subheader("Stock Return Correlation")

returns = data.pivot(
    index="Date",
    columns="Company",
    values="Close"
).pct_change()

correlation = returns.corr(min_periods=30)

if correlation.empty:
    st.info("Not enough overlapping data to calculate correlations.")
else:
    fig = px.imshow(
        correlation,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        aspect="auto",
        template="plotly_dark",
        title="Daily Return Correlation Matrix"
    )
    st.plotly_chart(fig, use_container_width=True)

st.caption(
    "Volatility and drawdown use historical prices. "
    "Correlation does not imply causation."
)
