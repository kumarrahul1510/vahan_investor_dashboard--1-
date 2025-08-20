
import pandas as pd
import numpy as np
import sqlite3
from typing import Optional, List

def load_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df

def load_from_sqlite(db_path: str) -> pd.DataFrame:
    con = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT date, state, vehicle_class, manufacturer, registrations FROM registrations", con)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        return df
    finally:
        con.close()

def yoy_qoq(df: pd.DataFrame, date_col="date", key_cols=("vehicle_class","manufacturer")) -> pd.DataFrame:
    d = df.copy()
    d[date_col] = pd.to_datetime(d[date_col])
    d = d.sort_values(date_col)
    monthly = d.groupby([pd.Grouper(key=date_col, freq="MS"), *key_cols], dropna=False)["registrations"].sum().reset_index()
    monthly = monthly.rename(columns={date_col:"date"})
    monthly["yoy_pct"] = monthly.groupby(list(key_cols), dropna=False)["registrations"].pct_change(12) * 100.0
    q = monthly.copy()
    q["quarter"] = q["date"].dt.to_period("Q")
    q = q.groupby(["quarter", *key_cols], dropna=False)["registrations"].sum().reset_index()
    q["qoq_pct"] = q.groupby(list(key_cols), dropna=False)["registrations"].pct_change(1) * 100.0
    monthly["quarter"] = monthly["date"].dt.to_period("Q")
    out = monthly.merge(q[["quarter", *key_cols, "qoq_pct"]], on=["quarter", *key_cols], how="left")
    return out

def filter_data(df: pd.DataFrame, date_from: Optional[pd.Timestamp], date_to: Optional[pd.Timestamp],
                classes: Optional[List[str]], manufacturers: Optional[List[str]], states: Optional[List[str]]) -> pd.DataFrame:
    d = df.copy()
    if date_from is not None:
        d = d[d["date"] >= pd.to_datetime(date_from)]
    if date_to is not None:
        d = d[d["date"] <= pd.to_datetime(date_to)]
    if classes:
        d = d[d["vehicle_class"].isin(classes)]
    if manufacturers:
        d = d[d["manufacturer"].isin(manufacturers)]
    if states and "All India (aggregate)" not in states:
        d = d[d["state"].isin(states)]
    return d

def topline_by_category(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"]).dt.to_period("M").dt.to_timestamp()
    cat = d.groupby([pd.Grouper(key="date", freq="MS"), "vehicle_class"])["registrations"].sum().reset_index()
    cat["yoy_pct"] = cat.groupby(["vehicle_class"])["registrations"].pct_change(12) * 100.0
    q = cat.copy()
    q["quarter"] = q["date"].dt.to_period("Q")
    q = q.groupby(["quarter", "vehicle_class"])["registrations"].sum().reset_index()
    q["qoq_pct"] = q.groupby(["vehicle_class"])["registrations"].pct_change(1) * 100.0
    cat["quarter"] = cat["date"].dt.to_period("Q")
    cat = cat.merge(q[["quarter","vehicle_class","qoq_pct"]], on=["quarter","vehicle_class"], how="left")
    return cat

def latest_period_changes(cat: pd.DataFrame) -> pd.DataFrame:
    last_date = cat["date"].max()
    latest = cat[cat["date"] == last_date][["vehicle_class","registrations","yoy_pct","qoq_pct"]].copy()
    return latest.sort_values("vehicle_class")

def market_share_over_time(df: pd.DataFrame) -> pd.DataFrame:
    """Return monthly manufacturer market share (%) across the filtered dataset."""
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"]).dt.to_period("M").dt.to_timestamp()
    monthly = d.groupby([pd.Grouper(key="date", freq="MS"), "manufacturer"])["registrations"].sum().reset_index()
    totals = monthly.groupby("date")["registrations"].sum().rename("total")
    monthly = monthly.merge(totals, on="date", how="left")
    monthly["share_pct"] = (monthly["registrations"] / monthly["total"] * 100.0).replace([np.inf, -np.inf], np.nan)
    return monthly
