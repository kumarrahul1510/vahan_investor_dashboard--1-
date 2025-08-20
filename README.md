
# Vahan Registration — Investor Dashboard (Streamlit)

Investor-friendly dashboard for vehicle registrations (2W/3W/4W) and manufacturer trends with YoY & QoQ growth.

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app ships with `sample_data.csv` so it runs out-of-the-box.

## Data Schema

| column         | type        | notes                                |
|----------------|-------------|--------------------------------------|
| date           | YYYY-MM-01  | first day of month for that period   |
| vehicle_class  | text        | 2W / 3W / 4W                         |
| manufacturer   | text        | e.g., Hero, Maruti, Tata             |
| registrations  | integer     | count of vehicle registrations       |

## Bringing Real Vahan Data

**Source:** Vahan Dashboard (MoRTH/NIC).

### Option A — Manual Export (Recommended)
1. Open the official Vahan dashboard.
2. Use filters to select time period (monthly view), vehicle class, and manufacturer.
3. Use the site's download/export (CSV/Excel) if available, or copy the table to CSV.
4. Normalize columns to match the schema above.
5. Save as `your_data.csv` and load it in the app via the sidebar.

### Option B — Programmatic Collection (Use responsibly)
If allowed by the site's Terms and robots.txt, inspect Network requests in DevTools to find JSON endpoints.
Use a polite `requests` client to fetch monthly series and save to CSV.

### SQL (Optional)
Use `db_setup.sql` to create a SQLite DB and `.import` your CSV into `registrations`. Point the app to this DB via the sidebar.

## Analytics Logic
- YoY%: Monthly vs same month last year.
- QoQ%: Quarterly totals vs previous quarter. The % is shown on each month of that quarter.

## Project Structure
- app.py — Streamlit UI
- etl.py — Data access & metrics
- db_setup.sql — SQLite schema (optional)
- sample_data.csv — Demo data
- requirements.txt
- README.md

## Disclaimer
Demo project; verify numbers with official sources before relying on them.


## 🚀 Deploy

Once pushed to GitHub, you can deploy on **Streamlit Community Cloud**:

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/<your-username>/vahan-investor-dashboard/main/app.py)

Replace `<your-username>` after you push the repo.

## State/UT Drilldown

The sample dataset includes a `state` column (e.g., Maharashtra, Uttar Pradesh, Gujarat, Tamil Nadu, Karnataka, Delhi).
Use the **State/UT** filter in the sidebar. Select **All India (aggregate)** for a national view, or one/multiple states to drill down.
