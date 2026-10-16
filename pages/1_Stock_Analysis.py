
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Stock Analysis | FinSight India",
    page_icon="📊",
    layout="wide"
)

st.markdown("""
<style>
.stApp { background-color: #0b1120; color: #f1f5f9; }
[data-testid="stMetric"] {
    background-color: #151f32;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #26364d;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("market_data.csv", parse_dates=["Date"])
    df = df.dropna(subset=["Date", "Close"])
    return df.sort_values(["Company", "Date"])

try:
    df = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(f"Could not load market_data.csv: {error}")
    st.stop()

st.title("📊 Stock Analysis")
st.caption("Explore individual company prices and trends.")

companies = sorted(df["Company"].unique())
company = st.selectbox("Select a company", companies)

stock = df[df["Company"] == company].copy()
stock = stock.sort_values("Date")

# Calculate moving averages across the full history
stock["20-Day Average"] = stock["Close"].rolling(20).mean()
stock["50-Day Average"] = stock["Close"].rolling(50).mean()

min_date = stock["Date"].min().date()
max_date = stock["Date"].max().date()

date_range = st.date_input(
    "Select analysis period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Please select both a start date and an end date.")
    st.stop()

start_date, end_date = date_range

if start_date > end_date:
    st.error("The start date must be before the end date.")
    st.stop()

stock = stock[
    stock["Date"].dt.date.between(start_date, end_date)
].copy()

if stock.empty:
    st.warning("No stock data is available for this period.")
    st.stop()

prices = stock["Close"].dropna()
returns = prices.pct_change().dropna()

period_return = (prices.iloc[-1] / prices.iloc[0] - 1) * 100
volatility = (
    returns.std() * np.sqrt(252) * 100
    if len(returns) > 1 else np.nan
)

running_max = prices.cummax()
drawdown = ((prices / running_max) - 1).min() * 100

c1, c2, c3 = st.columns(3)
c1.metric("Latest Price", f"₹{prices.iloc[-1]:,.2f}")
c2.metric("Period Return", f"{period_return:.2f}%")
c3.metric(
    "Annualized Volatility",
    f"{volatility:.2f}%" if pd.notna(volatility) else "N/A"
)

st.divider()
st.subheader(f"{company} — Price Trend")

fig = px.line(
    stock,
    x="Date",
    y=["Close", "20-Day Average", "50-Day Average"],
    template="plotly_dark",
    labels={
        "Date": "Date",
        "value": "Price (₹)",
        "variable": "Series"
    }
)
fig.update_layout(height=500, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.subheader("📉 Maximum Drawdown")
st.metric("Largest Peak-to-Trough Decline", f"{drawdown:.2f}%")

st.caption(
    "Moving averages smooth price fluctuations. "
    "Volatility and drawdown describe historical risk, "
    "not future performance."
)
