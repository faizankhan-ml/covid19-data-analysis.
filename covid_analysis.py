# covid_analysis.py
# A self-contained COVID-19 data analysis script.
# - If no CSV is provided, it uses an internal sample dataset.
# - Outputs: output/summary.txt and output/trend.png

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

def sample_dataframe() -> pd.DataFrame:
    """Create a small built-in dataset so the script works without any external files."""
    return pd.DataFrame({
        "country": ["Germany","Germany","Germany","Pakistan","Pakistan","Pakistan"],
        "date":    ["2021-01-01","2021-06-01","2021-12-01","2021-01-01","2021-06-01","2021-12-01"],
        "cases":   [1800000, 3700000, 6000000, 480000,  940000,  1300000],
        "deaths":  [35000,   89000,   100000,  10000,   22000,   28000]
    })

def load_data(csv_path: str | None) -> pd.DataFrame:
    """
    Load CSV if path is provided and exists; otherwise return a sample DataFrame.
    Expected columns: country,date,cases,deaths
    """
    if csv_path and os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
    else:
        df = sample_dataframe()

    # Normalize column names
    df.columns = [c.lower() for c in df.columns]

    required = {"country", "date", "cases", "deaths"}
    if not required.issubset(df.columns):
        raise ValueError(f"CSV must include columns: {required}")

    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning + typing + sorting."""
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["cases"] = pd.to_numeric(df["cases"], errors="coerce")
    df["deaths"] = pd.to_numeric(df["deaths"], errors="coerce")

    df = df.dropna(subset=["country", "date", "cases", "deaths"])
    df = df.sort_values(["country", "date"]).reset_index(drop=True)
    return df

def make_summary(df: pd.DataFrame, outdir: str) -> str:
    """Write a concise summary.txt with key stats."""
    lines = []
    lines.append("COVID-19 Data Analysis Summary\n")
    lines.append(f"Countries: {df['country'].nunique()}")
    try:
        dmin = df["date"].min().date()
        dmax = df["date"].max().date()
        lines.append(f"Date range: {dmin} to {dmax}\n")
    except Exception:
        lines.append("Date range: (unavailable)\n")

    lines.append("Max Cases by Country:")
    lines.append(str(df.groupby("country")["cases"].max()))

    lines.append("\nMax Deaths by Country:")
    lines.append(str(df.groupby("country")["deaths"].max()))

    path = os.path.join(outdir, "summary.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path

def plot_trend(df: pd.DataFrame, outdir: str) -> str:
    """
    Plot cases trend by country.
    One simple line per country (no custom colors/styles).
    """
    plt.figure(figsize=(9, 5))
    for country, g in df.groupby("country"):
        g = g.sort_values("date")
        # Convert dates to strings for x-axis readability
        plt.plot(g["date"].astype(str), g["cases"], marker="o", label=country)

    plt.title("COVID-19 Cases Trend by Country")
    plt.xlabel("Date")
    plt.ylabel("Cases")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    path = os.path.join(outdir, "trend.png")
    plt.savefig(path)
    return path

def parse_args():
    """
    Minimal arg parsing without external libraries.
    Usage:
      python covid_analysis.py --csv your_data.c
