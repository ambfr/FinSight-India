
import streamlit as st
import pandas as pd
import plotly.express as px

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #f1f5f9;
}
[data-testid="stMetric"] {
    background-color: #151f32;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #26364d;
}
h1, h2, h3 {
    color: #f1f5f9;
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


st.title("📈 FinSight India")
st.caption("Indian Equity Market | Performance, Risk & Analytics")

st.sidebar.markdown("## FinSight India")
st.sidebar.caption("Explore Indian stock market data")

companies = sorted(df["Company"].unique())

selected = st.multiselect(
    "Choose companies to compare",
    companies,
    default=companies[:5]
)

if not selected:
    st.info("Select at least one company to view the dashboard.")
    st.stop()

data = df[df["Company"].isin(selected)].copy()

metrics = []

for company, group in data.groupby("Company"):
    group = group.sort_values("Date")
    prices = group["Close"].dropna()

    if len(prices) < 2:
        continue

    metrics.append({
        "Company": company,
        "Latest Price": prices.iloc[-1],
        "Period Return (%)": (
            prices.iloc[-1] / prices.iloc[0] - 1
        ) * 100
    })

metrics_df = pd.DataFrame(metrics)

if not metrics_df.empty:
    best = metrics_df.loc[
        metrics_df["Period Return (%)"].idxmax()
    ]

    c1, c2, c3 = st.columns(3)
    c1.metric("Companies Selected", len(metrics_df))
    c2.metric("Best Performer", best["Company"])
    c3.metric(
        "Best Period Return",
        f"{best['Period Return (%)']:.2f}%"
    )

st.divider()

st.subheader("📊 Relative Stock Performance")
st.caption(
    "Each selected stock starts at 100 to compare percentage changes."
)

data["Indexed Price"] = (
    data["Close"]
    / data.groupby("Company")["Close"].transform("first")
    * 100
)

fig = px.line(
    data,
    x="Date",
    y="Indexed Price",
    color="Company",
    template="plotly_dark",
    labels={
        "Date": "Date",
        "Indexed Price": "Indexed Price (Base = 100)",
        "Company": "Company"
    }
)

fig.update_layout(height=480, hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

st.subheader("🏆 Company Performance")

if not metrics_df.empty:
    display = metrics_df.sort_values(
        "Period Return (%)",
        ascending=False
    ).copy()

    display["Latest Price"] = display["Latest Price"].round(2)
    display["Period Return (%)"] = (
        display["Period Return (%)"].round(2)
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True
    )

st.caption(
    "Source: Historical market data retrieved using yfinance. "
    "Historical performance does not predict future results."
)
