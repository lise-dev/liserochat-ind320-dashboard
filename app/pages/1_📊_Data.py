import streamlit as st
import pandas as pd
from pathlib import Path

from utils.common import (
    resolve_csv_path,
    load_time_indexed_data,
    list_distinct_month_strings_from_index,
    list_numeric_columns,
    prettify_column_name,
    make_unique,
)

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(page_title="Data", layout="wide")


def main():
    # ---------------- PAGE HEADER ----------------
    st.title("Data")
    st.caption(
        "One row per imported numeric column. Each row shows a sparkline "
        "for the **first month** of the time series."
    )

    # ---------------- LOAD CSV DATA ----------------
    # Resolve project root and CSV file location
    project_root = Path(__file__).resolve().parents[1]
    csv_file_path = resolve_csv_path(project_root)

    # Load the time-indexed dataset (cached for faster reloads)
    time_indexed_data = load_time_indexed_data(csv_file_path)

    # Display basic dataset info
    st.caption(f"Rows: {time_indexed_data.shape[0]:,}  |  Columns: {time_indexed_data.shape[1]:,}")

    # ---------------- DATASET OVERVIEW ----------------
    st.subheader("Dataset overview")

    # Expandable section showing descriptive statistics (numeric columns only)
    with st.expander("Descriptive statistics"):
        desc = time_indexed_data.describe().T  # count, mean, std, min, quartiles, max
        st.dataframe(desc, use_container_width=True)

    # Compute time coverage, number of months, and shape
    month_strings = time_indexed_data.index.to_period("M").astype(str)
    time_min = time_indexed_data.index.min()
    time_max = time_indexed_data.index.max()
    n_months = len(pd.Index(month_strings).unique())

    # Display summary information below stats
    st.caption(
        f"Time coverage: {time_min.strftime('%Y-%m-%d')} → {time_max.strftime('%Y-%m-%d')} "
        f"| Distinct months: {n_months} "
        f"| Rows: {time_indexed_data.shape[0]:,} "
        f"| Columns: {time_indexed_data.shape[1]:,}"
    )

    # ---------------- MISSING VALUES CHECK ----------------
    na_counts = time_indexed_data.isna().sum()
    if int(na_counts.sum()) > 0:
        st.caption("Missing values per column:")
        st.dataframe(
            na_counts[na_counts > 0].rename("Missing").to_frame(),
            use_container_width=True
        )
    else:
        st.caption("No missing values detected.")

    # ---------------- FIRST MONTH SUBSET ----------------
    # Extract the first available month to build the summary table below
    months = list_distinct_month_strings_from_index(time_indexed_data)
    if not months:
        st.warning("No valid months derived from the time index.")
        return
    first_month = months[0]
    st.subheader(f"First month subset: {first_month}")

    # Filter data to the first month
    month_strings = time_indexed_data.index.to_period("M").astype(str)
    mask_first = (month_strings == first_month)
    first_month_data = time_indexed_data.loc[mask_first].copy()

    # Keep only numeric columns
    numeric_cols = list_numeric_columns(first_month_data)
    if not numeric_cols:
        st.info("No numeric columns found in the dataset.")
        return

    # ---------------- TABLE PREPARATION ----------------
    # Create one row per variable, with sparkline data and summary values
    rows_for_display: list[dict] = []
    for col in numeric_cols:
        series = first_month_data[col].astype(float)
        rows_for_display.append(
            {
                "Variable": prettify_column_name(col),
                "Row trend": series.tolist(),        # values for sparkline
                "Min": float(series.min()),
                "Mean": float(series.mean()),
                "Max": float(series.max()),
            }
        )

    # Build dataframe for display and ensure column names are unique
    display_df = pd.DataFrame(rows_for_display)
    display_df.columns = make_unique(list(display_df.columns))

    # ---------------- DISPLAY TABLE ----------------
    # Interactive table with mini line charts per variable
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            "Row trend": st.column_config.LineChartColumn(
                "Row trend (first month)",
                help="Mini line chart over the first month for this variable."
            ),
            "Variable": st.column_config.TextColumn("Variable"),
            "Min": st.column_config.NumberColumn("Min"),
            "Mean": st.column_config.NumberColumn("Mean"),
            "Max": st.column_config.NumberColumn("Max"),
        }
    )


if __name__ == "__main__":
    main()
