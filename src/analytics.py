
import pandas as pd
import numpy as np


def calculate_daily_returns(df):
    df = df.copy()
    df = df.sort_values(["Company", "Date"])

    df["Daily Return"] = (
        df.groupby("Company")["Close"].pct_change()
    )

    df["Cumulative Return"] = (
        (1 + df["Daily Return"])
        .groupby(df["Company"])
        .cumprod() - 1
    )

    return df


def calculate_company_metrics(df):
    results = []

    for company, group in df.groupby("Company"):
        group = group.sort_values("Date").copy()

        prices = group["Close"].dropna()
        returns = prices.pct_change().dropna()

        if len(prices) < 2 or returns.empty:
            continue

        running_max = prices.cummax()
        drawdowns = prices / running_max - 1

        results.append({
            "Company": company,
            "Latest Price": prices.iloc[-1],
            "Period Return (%)": (
                prices.iloc[-1] / prices.iloc[0] - 1
            ) * 100,
            "Annualized Volatility (%)": (
                returns.std() * np.sqrt(252) * 100
            ),
            "Maximum Drawdown (%)": drawdowns.min() * 100,
            "Trading Days": len(prices)
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    stocks = pd.read_csv("market_data.csv", parse_dates=["Date"])

    stocks = calculate_daily_returns(stocks)
    metrics = calculate_company_metrics(stocks)

    print("\nFINANCIAL PERFORMANCE SUMMARY\n")
    print(metrics.round(2).to_string(index=False))

    stocks.to_csv("market_data.csv", index=False)
    metrics.to_csv("company_metrics.csv", index=False)

    print("\nSaved market_data.csv and company_metrics.csv")
