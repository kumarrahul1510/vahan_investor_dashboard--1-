
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from etl import load_csv, load_from_sqlite, yoy_qoq, filter_data, topline_by_category, latest_period_changes, market_share_over_time

st.set_page_config(page_title="Vahan: Investor Dashboard", layout="wide")

st.title("Vahan Registration Dashboard — Investor View")
st.caption("Focus: Vehicle-class & Manufacturer trends with YoY / QoQ growth")

with st.expander("Data Source & Instructions", expanded=False):
    st.markdown(
        "**Source:** Vahan Dashboard (MoRTH), India.\n\n"
        "- Export monthly registration data by **Vehicle Class** and **Manufacturer** from the Vahan Dashboard (CSV if available).  \n"
        "- Required columns: `date (YYYY-MM-01)`, `state`, `vehicle_class (2W/3W/4W)`, `manufacturer`, `registrations` (integer).  \n"
        "- You can load from a CSV or a local SQLite DB created from CSV. See README for details."
    )

source = st.sidebar.radio("Data source", ["CSV", "SQLite (optional)"], index=0)
if source == "CSV":
    uploaded = st.sidebar.file_uploader("Upload CSV (date, state, vehicle_class, manufacturer, registrations)", type=["csv"])
    if uploaded is not None:
        df = pd.read_csv(uploaded)
        df["date"] = pd.to_datetime(df["date"])
    else:
        st.sidebar.info("No file uploaded — using bundled sample_data.csv")
        df = load_csv("sample_data.csv")
else:
    db_path = st.sidebar.text_input("SQLite DB path", "vahan.db")
    try:
        df = load_from_sqlite(db_path)
    except Exception as e:
        st.sidebar.warning(f"Failed to read DB; falling back to sample_data.csv. Error: {e}")
        df = load_csv("sample_data.csv")

# --- Sidebar filters
min_date = df["date"].min().date()
max_date = df["date"].max().date()
date_range = st.sidebar.date_input("Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple):
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

classes = sorted(df["vehicle_class"].unique().tolist())
manufacturers = sorted(df["manufacturer"].unique().tolist())
states = sorted(df["state"].unique().tolist())
states = ["All India (aggregate)"] + states

sel_classes = st.sidebar.multiselect("Vehicle categories", classes, default=classes)
sel_mfrs = st.sidebar.multiselect("Manufacturers", manufacturers)  # default: all
sel_states = st.sidebar.multiselect("State/UT", states, default=["All India (aggregate)"])

filtered = filter_data(df, start_date, end_date, sel_classes, sel_mfrs, sel_states)

# --- KPI cards (Topline by category)
cat = topline_by_category(filtered)
latest = latest_period_changes(cat)

st.subheader("Topline — Latest Month by Category")
show_classes = sel_classes if sel_classes else classes
kpi_cols = st.columns(len(show_classes) if show_classes else 1)
for i, c in enumerate(sorted(show_classes)):
    with kpi_cols[i]:
        row = latest[latest["vehicle_class"] == c]
        if len(row):
            val = int(row["registrations"].iloc[0])
            yoy = row["yoy_pct"].iloc[0]
            qoq = row["qoq_pct"].iloc[0]
            yoy_str = "—" if pd.isna(yoy) else f"{yoy:+.1f}%"
            qoq_str = "—" if pd.isna(qoq) else f"{qoq:+.1f}%"
            st.metric(f"{c} registrations", f"{val:,}", help="Latest month total within selected filters")
            st.caption(f"YoY: {yoy_str} | QoQ: {qoq_str}")
        else:
            st.metric(f"{c} registrations", "—")
            st.caption("YoY: — | QoQ: —")

# --- Trends
st.subheader("Trends")
tab1, tab2, tab3 = st.tabs(["By Vehicle Category", "By Manufacturer", "Market Share"])

with tab1:
    st.markdown("**Monthly registrations by category**")
    if len(cat):
        pivot_cat = cat.pivot_table(index="date", columns="vehicle_class", values="registrations", aggfunc="sum")
        st.line_chart(pivot_cat, height=360)
    st.markdown("**YoY % by category (monthly)**")
    if len(cat):
        pivot_yoy = cat.pivot_table(index="date", columns="vehicle_class", values="yoy_pct")
        st.line_chart(pivot_yoy, height=280)
    st.markdown("**QoQ % by category (quarterly, shown on each month of the quarter)**")
    if len(cat):
        pivot_qoq = cat.pivot_table(index="date", columns="vehicle_class", values="qoq_pct")
        st.line_chart(pivot_qoq, height=280)

with tab2:
    st.markdown("**Monthly registrations by manufacturer**")
    m = yoy_qoq(filtered)
    if len(m):
        top_mfrs = (m.groupby("manufacturer")["registrations"].sum().sort_values(ascending=False).head(12).index.tolist()
                    if not sel_mfrs else sel_mfrs)
        m_view = m[m["manufacturer"].isin(top_mfrs)]
        pivot_m = m_view.pivot_table(index="date", columns="manufacturer", values="registrations", aggfunc="sum")
        st.line_chart(pivot_m, height=360)

        st.markdown("**YoY % by manufacturer (monthly)**")
        pivot_my = m_view.pivot_table(index="date", columns="manufacturer", values="yoy_pct")
        st.line_chart(pivot_my, height=280)

        st.markdown("**QoQ % by manufacturer (quarterly, shown on each month of the quarter)**")
        pivot_mq = m_view.pivot_table(index="date", columns="manufacturer", values="qoq_pct")
        st.line_chart(pivot_mq, height=280)

with tab3:
    st.markdown("**Manufacturer Market Share**")
    share_df = market_share_over_time(filtered)
    if len(share_df):
        # Line chart of share % over time for top 8 manufacturers
        top_by_total = (share_df.groupby("manufacturer")["registrations"].sum()
                        .sort_values(ascending=False).head(8).index.tolist())
        share_view = share_df[share_df["manufacturer"].isin(top_by_total)]
        pivot_share = share_view.pivot_table(index="date", columns="manufacturer", values="share_pct")
        st.line_chart(pivot_share, height=360)

        # Pie of latest month (top-8 + Others)
        latest_date = share_df["date"].max()
        latest_slice = share_df[share_df["date"] == latest_date]
        latest_slice = latest_slice.sort_values("share_pct", ascending=False)
        top = latest_slice[latest_slice["manufacturer"].isin(top_by_total)]
        others_pct = max(0.0, 100.0 - top["share_pct"].sum())
        labels = top["manufacturer"].tolist() + (["Others"] if others_pct > 0 else [])
        sizes = top["share_pct"].tolist() + ([others_pct] if others_pct > 0 else [])

        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct=lambda p: f"{p:.1f}%" if p >= 1 else "")
        ax.set_title(f"Market Share — {latest_date.strftime('%b %Y')}")
        st.pyplot(fig)

# --- Data Table
with st.expander("Show filtered data table"):
    st.dataframe(filtered.sort_values("date"), use_container_width=True)

st.divider()
st.caption("© 2025 Investor demo. Not affiliated with or endorsed by MoRTH/NIC. For illustration only.")
