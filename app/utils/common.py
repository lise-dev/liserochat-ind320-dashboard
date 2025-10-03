# utils/common.py
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------- PATH HELPERS ----------------
def resolve_csv_path(project_root_directory: Path) -> Path:
    """Return the default CSV location."""
    return project_root_directory / "data" / "open-meteo-subset.csv"


# ------------- DATA LOADING (CACHED) ----------
@st.cache_data(show_spinner=True)
def load_time_indexed_data(csv_file_path: Path) -> pd.DataFrame:
    """
    Load CSV like in the notebook:
    - encoding='utf-8'
    - sep=','
    - parse 'time' in UTC
    - sort by time and set as index
    - drop duplicate columns if any
    """
    data_frame = pd.read_csv(csv_file_path, encoding="utf-8-sig", sep=",")

    if data_frame.columns.duplicated().any():
        data_frame = data_frame.loc[:, ~data_frame.columns.duplicated()].copy()

    if "time" not in data_frame.columns:
        raise KeyError("The 'time' column is missing from the dataset.")

    data_frame["time"] = pd.to_datetime(data_frame["time"], errors="coerce", utc=True)
    data_frame = data_frame.sort_values("time").reset_index(drop=True)
    data_frame = data_frame.set_index("time")
    return data_frame


# ------------- MONTH HELPERS ------------------
def list_distinct_month_strings_from_index(time_indexed_data: pd.DataFrame) -> list[str]:
    """Return YYYY-MM strings sorted."""
    month_strings = time_indexed_data.index.to_period("M").astype(str)
    return sorted(pd.Index(month_strings).unique().tolist())

def filter_by_month_range(time_indexed_data: pd.DataFrame, start_month: str, end_month: str) -> pd.DataFrame:
    """Filter rows whose month (YYYY-MM) is in [start_month, end_month]."""
    month_strings = time_indexed_data.index.to_period("M").astype(str)
    mask = (month_strings >= start_month) & (month_strings <= end_month)
    return time_indexed_data.loc[mask].copy()


# ------------- COLUMN HELPERS -----------------
def list_numeric_columns(data_frame: pd.DataFrame) -> list[str]:
    """Return only numeric column names."""
    return data_frame.select_dtypes(include="number").columns.tolist()

def prettify_column_name(original: str) -> str:
    """
    Make a column name user-friendly:
    - Replace '_' with space
    - Add space between number and 'm' (10m -> 10 m)
    - Keep units in parentheses as-is
    - Title Case the base name
    """
    if not isinstance(original, str):
        original = str(original)

    # Split base vs units "(...)"
    match = re.match(r"^(.*?)(\s*\(.*\)\s*)$", original.strip())
    if match:
        base, units = match.group(1), match.group(2)
    else:
        base, units = original.strip(), ""

    base = base.replace("_", " ")
    base = re.sub(r"(\d+)(m)\b", r"\1 \2", base, flags=re.IGNORECASE)
    base = re.sub(r"\s+", " ", base).strip().title()

    return f"{base}{units}"

def make_unique(names: list[str]) -> list[str]:
    """Ensure unique names by appending (2), (3), ... if needed."""
    seen = {}
    unique = []
    for n in names:
        if n not in seen:
            seen[n] = 1
            unique.append(n)
        else:
            seen[n] += 1
            unique.append(f"{n} ({seen[n]})")
    return unique

def build_pretty_name_mappings(column_names: list[str]) -> tuple[dict, dict, list[str]]:
    """
    Return mappings for nice labels:
      - original_to_pretty
      - pretty_to_original
      - pretty_names list (unique and ordered)
    """
    pretties = [prettify_column_name(c) for c in column_names]
    pretties = make_unique(pretties)
    original_to_pretty = dict(zip(column_names, pretties))
    pretty_to_original = dict(zip(pretties, column_names))
    return original_to_pretty, pretty_to_original, pretties


# ------------- SCALING HELPERS ----------------
def scale_numeric_frame(frame: pd.DataFrame, column_names: list[str], method: str = "raw"):
    """
    Return a copy with selected columns scaled.
    method: 'raw' | 'zscore' | 'minmax' | 'log1p'
    """
    scaled = frame.copy()
    if method == "raw":
        return scaled, "Values"

    for col in column_names:
        series = scaled[col].astype(float)
        if method == "zscore":
            std = series.std()
            scaled[col] = (series - series.mean()) / (std if std != 0 else 1.0)
        elif method == "minmax":
            rng = series.max() - series.min()
            scaled[col] = (series - series.min()) / (rng if rng != 0 else 1.0)
        elif method == "log1p":
            # Clip negatives to 0 for log, log1p handles zeros
            scaled[col] = np.log1p(series.clip(lower=0))
        else:
            scaled[col] = series

    ylabel = {
        "raw": "Values",
        "zscore": "Z-score",
        "minmax": "Scaled 0–1",
        "log1p": "log1p(value)",
    }.get(method, "Values")
    return scaled, ylabel


# ------------- PLOTTING HELPERS --------------
def plot_single_series_matplotlib(time_indexed_data: pd.DataFrame, column_name: str, figure_size=(9, 4)):
    """One line chart for a single column vs time."""
    fig, ax = plt.subplots(figsize=figure_size)
    ax.plot(time_indexed_data.index, time_indexed_data[column_name])
    ax.set_title(f"{column_name} vs time")
    ax.set_xlabel("Time")
    ax.set_ylabel(column_name)
    ax.grid(True)
    fig.tight_layout()
    return fig

def plot_all_series_with_optional_secondary_axis(
    time_indexed_data: pd.DataFrame,
    primary_columns: list[str],
    secondary_columns: list[str] | None = None,
    ylabel_left: str = "Values",
    ylabel_right: str = "Values",
    figure_size=(11, 6),
):
    """
    Plot all columns. If `secondary_columns` is given, those are drawn on a right Y-axis.
    Useful to put wind direction (°) on the secondary axis.
    """
    fig, ax_left = plt.subplots(figsize=figure_size)
    ax_right = None

    # Left axis
    for c in primary_columns:
        ax_left.plot(time_indexed_data.index, time_indexed_data[c], label=c)
    ax_left.set_xlabel("Time")
    ax_left.set_ylabel(ylabel_left)
    ax_left.grid(True)

    # Right axis (optional)
    if secondary_columns:
        ax_right = ax_left.twinx()
        for c in secondary_columns:
            ax_right.plot(time_indexed_data.index, time_indexed_data[c], linestyle="--", label=c)
        ax_right.set_ylabel(ylabel_right)

    # Combine legends
    h_left, l_left = ax_left.get_legend_handles_labels()
    if ax_right:
        h_right, l_right = ax_right.get_legend_handles_labels()
        handles = h_left + h_right
        labels = l_left + l_right
    else:
        handles, labels = h_left, l_left

    ax_left.legend(handles, labels, loc="best")
    title = "All numeric columns as a function of time"
    if secondary_columns:
        title += " (secondary axis used)"
    ax_left.set_title(title)
    fig.tight_layout()
    return fig
