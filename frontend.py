import os
import streamlit as st
import requests
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/sales")
API_KEY = os.getenv("API_KEY", "")
HEADERS = {"X-API-Key": API_KEY}

st.set_page_config(
    page_title="SalesTelemetry",
    page_icon="📊",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }

[data-testid="metric-container"] {
    background: #f9f9f7;
    border: 1px solid #e8e8e4;
    border-radius: 8px;
    padding: 1rem 1.25rem;
}
[data-testid="metric-container"] label {
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #888;
    font-family: 'DM Mono', monospace;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem;
    font-weight: 500;
    color: #111;
}
.section-label {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #aaa;
    font-family: 'DM Mono', monospace;
    margin-bottom: 0.5rem;
    margin-top: 2rem;
}
[data-testid="stFileUploader"] {
    border: 1.5px dashed #ddd;
    border-radius: 8px;
    padding: 0.5rem;
    background: #fafafa;
}
hr { border: none; border-top: 1px solid #eee; margin: 2rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## SalesTelemetry")
st.markdown(
    "<p style='color:#888; margin-top:-0.5rem; margin-bottom:2rem;'>Retail analytics dashboard</p>",
    unsafe_allow_html=True,
)

# ── API Key Gate ──────────────────────────────────────────────────────────────
# If API_KEY isn't set via env var, let the user enter it in the sidebar
if not API_KEY:
    with st.sidebar:
        st.markdown("### Authentication")
        entered_key = st.text_input("API Key", type="password", placeholder="Enter your API key")
        if entered_key:
            HEADERS = {"X-API-Key": entered_key}
        else:
            st.warning("Enter your API key to continue.")
            st.stop()

# ── Upload ────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>Dataset</div>", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload a sales CSV to get started",
    type=["csv"],
    label_visibility="collapsed",
)

if uploaded_file:
    with st.spinner("Loading dataset..."):
        res = requests.post(
            f"{API_BASE}/upload",
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")},
            headers=HEADERS,
        )

    if res.status_code == 200:
        data = res.json()
        st.success(f"✓ {data['rows_loaded']:,} rows loaded from **{data['filename']}**")
    elif res.status_code == 403:
        st.error("Invalid API key.")
        st.stop()
    else:
        try:
            detail = res.json().get("detail", res.text)
        except Exception:
            detail = res.text
        st.error(f"Upload failed: {detail}")
        st.stop()

st.markdown("<hr>", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>KPIs</div>", unsafe_allow_html=True)

country_filter = st.text_input(
    "Filter by country (leave blank for all)",
    placeholder="e.g. United States",
)

try:
    params = {"country": country_filter} if country_filter else {}
    kpi_res = requests.get(f"{API_BASE}/kpis", params=params, headers=HEADERS)
    kpis = kpi_res.json()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Revenue", f"${kpis['total_revenue']:,.0f}")
    col2.metric("Total Profit", f"${kpis['total_profit']:,.0f}")
    col3.metric("Total Cost", f"${kpis['total_cost']:,.0f}")
    col4.metric("Purchases", f"{kpis['number_of_purchases']:,}")
    col5.metric("Profit Margin", f"{kpis['profit_margin']}%")

except Exception:
    st.info("Upload a dataset to see KPIs.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Records ───────────────────────────────────────────────────────────────────
st.markdown("<div class='section-label'>Records</div>", unsafe_allow_html=True)

with st.expander("Filters", expanded=False):
    fc1, fc2, fc3, fc4 = st.columns(4)
    f_country = fc1.text_input("Country", key="rec_country")
    f_category = fc2.text_input("Product Category", key="rec_category")
    f_date_from = fc3.text_input("Date From (YYYY-MM-DD)", key="rec_from")
    f_date_to = fc4.text_input("Date To (YYYY-MM-DD)", key="rec_to")

try:
    params = {
        "limit": 500,
        **({"country": f_country} if f_country else {}),
        **({"product_category": f_category} if f_category else {}),
        **({"date_from": f_date_from} if f_date_from else {}),
        **({"date_to": f_date_to} if f_date_to else {}),
    }
    rec_res = requests.get(f"{API_BASE}/", params=params, headers=HEADERS)
    records = rec_res.json()

    if records:
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.rename(columns={
            "id": "ID", "date": "Date", "country": "Country",
            "state": "State", "product_category": "Category",
            "order_quantity": "Qty", "unit_cost": "Unit Cost",
            "unit_price": "Unit Price", "profit": "Profit", "revenue": "Revenue",
        })
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"{len(records):,} records shown (max 500)")
    else:
        st.info("No records found.")

except Exception:
    st.info("Upload a dataset to browse records.")
