
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "market_data.csv"

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


def refresh_market_data():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Could not find existing dataset: {CSV_PATH}"
        )

    existing = pd.read_csv(CSV_PATH, parse_dates=["Date"])

    required = {"Date", "Company", "Ticker", "Close"}
    missing = required - set(existing.columns)

    if missing:
        raise ValueError(
            f"market_data.csv is missing required columns: {missing}"
        )

    existing["Date"] = pd.to_datetime(existing["Date"]).dt.normalize()

    latest_date = existing["Date"].max()
    today = pd.Timestamp(date.today())

    # Re-fetch recent dates to fill gaps and update overlapping records.
    start_date = min(
        latest_date - pd.Timedelta(days=7),
        today - pd.Timedelta(days=14)
    ).date()

    # yfinance's end date is exclusive.
    end_date = (date.today() + timedelta(days=1)).isoformat()

    new_frames = []
    failures = []

    for company, ticker in COMPANIES.items():
        try:
            history = yf.Ticker(ticker).history(
                start=start_date.isoformat(),
                end=end_date,
                interval="1d",
                auto_adjust=True
            )

            if history.empty or "Close" not in history.columns:
                failures.append(f"{company}: no data returned")
                continue

            history = history.reset_index()

            if "Date" not in history.columns:
                history = history.rename(
                    columns={history.columns[0]: "Date"}
                )

            dates = pd.to_datetime(history["Date"])

            if dates.dt.tz is not None:
                dates = dates.dt.tz_localize(None)

            history["Date"] = dates.dt.normalize()
            history["Company"] = company
            history["Ticker"] = ticker

            # Keep the existing CSV's columns and their order.
            # With auto_adjust=True, Close is adjusted; if the existing
            # CSV has Adj Close, use Close for the new rows as well.
            if "Adj Close" in existing.columns:
                history["Adj Close"] = history["Close"]

            for column in existing.columns:
                if column not in history.columns:
                    history[column] = pd.NA

            new_frames.append(history[existing.columns])

        except Exception as error:
            failures.append(f"{company}: {error}")

    if not new_frames:
        details = "\n".join(failures)
        raise RuntimeError(
            "No updated data could be retrieved. "
            "Your existing CSV has not been changed.\n" + details
        )

    new_data = pd.concat(new_frames, ignore_index=True)
    new_data = new_data.dropna(subset=["Date", "Close"])

    key_columns = ["Date", "Company", "Ticker"]

    old_keys = set(
        map(tuple, existing[key_columns].astype(str).to_numpy())
    )

    new_keys = set(
        map(tuple, new_data[key_columns].astype(str).to_numpy())
    )

    rows_added = len(new_keys - old_keys)

    combined = pd.concat(
        [existing, new_data],
        ignore_index=True
    )

    combined = combined.drop_duplicates(
        subset=key_columns,
        keep="last"
    )

    combined = combined.sort_values(
        ["Date", "Company"]
    ).reset_index(drop=True)

    # Write only after at least one ticker returned usable data.
    combined.to_csv(CSV_PATH, index=False)

    return {
        "rows_added": rows_added,
        "tickers_updated": len(new_frames),
        "failures": failures,
        "latest_date": combined["Date"].max().strftime("%Y-%m-%d"),
    }
