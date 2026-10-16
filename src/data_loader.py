
import yfinance as yf
import pandas as pd

COMPANIES = {
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "State Bank of India": "SBIN.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "Reliance Industries": "RELIANCE.NS",
    "ONGC": "ONGC.NS",
    "ITC": "ITC.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "Mahindra & Mahindra": "M&M.NS",
}


def fetch_stock_data(period="2y"):
    frames = []

    for company, ticker in COMPANIES.items():
        try:
            df = yf.Ticker(ticker).history(
                period=period,
                auto_adjust=True
            )

            if df.empty:
                print(f"No data returned for {company}")
                continue

            df = df.reset_index()
            df["Company"] = company
            df["Ticker"] = ticker
            frames.append(df)

        except Exception as error:
            print(f"Could not fetch {company}: {error}")

    if not frames:
        raise RuntimeError(
            "No market data was retrieved. Check your connection "
            "and ticker availability."
        )

    result = pd.concat(frames, ignore_index=True)
    result["Date"] = pd.to_datetime(result["Date"]).dt.tz_localize(None)
    result = result.sort_values(["Company", "Date"])

    return result


if __name__ == "__main__":
    stocks = fetch_stock_data()
    print(stocks.head())
    print(f"\nRows retrieved: {len(stocks)}")
    print(f"Companies retrieved: {stocks['Company'].nunique()}")

    stocks.to_csv("market_data.csv", index=False)
    print("Saved market_data.csv")
