
import streamlit as st
from src.refresh_data import refresh_market_data
from datetime import datetime

st.set_page_config(
    page_title="FinSight India",
    page_icon="📈",
    layout="wide"
)

pages = {
    "Dashboard": [
        st.Page("pages/0_Overview.py", title="Overview", icon="🏠", default=True),
    ],
    "Analytics": [
        st.Page("pages/1_Stock_Analysis.py", title="Stock Analysis", icon="📊"),
        st.Page("pages/2_Sector_Analysis.py", title="Sector Analysis", icon="🏭"),
        st.Page("pages/3_Risk_Correlation.py", title="Risk & Correlation", icon="📉"),
        st.Page("pages/4_Data_Explorer.py", title="Data Explorer", icon="🗂️"),
        st.Page("pages/5_Data_Quality.py",title="Data Quality",icon="🔎"),
    ],
}


pg = st.navigation(pages)

st.sidebar.divider()
st.sidebar.subheader("Market Data")

if st.sidebar.button("🔄 Refresh Market Data", use_container_width=True):
    with st.spinner("Fetching updated stock data..."):
        try:
            result = refresh_market_data()
            st.session_state["last_refreshed"] = (
                datetime.now().strftime("%d %b %Y, %I:%M:%S %p")
            )
            

            # Clear cached CSV data so every page reloads the updated file.
            st.cache_data.clear()

            st.sidebar.success(
                f"Updated {result['tickers_updated']} companies. "
                f"New rows added: {result['rows_added']}. "
                f"Latest date: {result['latest_date']}"
            )

            if result["failures"]:
                st.sidebar.warning(
                    "Some companies could not be refreshed:\n"
                    + "\n".join(result["failures"])
                )

        except Exception as error:
            st.sidebar.error(f"Refresh failed: {error}")

        if st.session_state.get("last_refreshed"):
            st.sidebar.caption(
                "Last refreshed: "
                + st.session_state["last_refreshed"]
            )
        else:
            st.sidebar.caption("Last refreshed: Not yet refreshed")

pg.run()

