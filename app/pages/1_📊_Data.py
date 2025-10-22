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

st.set_page_config(page_title="Data", layout="wide")

def main():
    st.title("Data")
    st.caption(
        "One row per imported numeric column. Each row shows a sparkline "
        "for the **first month** of the time series."
    )

    project_root = Path(__file__).resolve().parents[1]
    csv_file_path = resolve_csv_path(project_root)

    time_indexed_data = load_time_indexed_data(csv_file_path)
    st.caption(f"Rows: {time_indexed_data.shape[0]:,}  |  Columns: {time_indexed_data.shape[1]:,}")

    # === Dataset overview ===
    st.subheader("Dataset overview")

    # Descriptive stats (numeric)
    with st.expander("Descriptive statistics"):
        desc = time_indexed_data.describe().T  # count, mean, std, min, quartiles, max
        st.dataframe(desc, use_container_width=True)

    # Coverage, months, shape
    month_strings = time_indexed_data.index.to_period("M").astype(str)
    time_min = time_indexed_data.index.min()
    time_max = time_indexed_data.index.max()
    n_months = len(pd.Index(month_strings).unique())

    st.caption(
        f"Time coverage: {time_min.strftime('%Y-%m-%d')} → {time_max.strftime('%Y-%m-%d')} "
        f"| Distinct months: {n_months} "
        f"| Rows: {time_indexed_data.shape[0]:,} "
        f"| Columns: {time_indexed_data.shape[1]:,}"
    )

    # Missing values (only show if any)
    na_counts = time_indexed_data.isna().sum()
    if int(na_counts.sum()) > 0:
        st.caption("Missing values per column:")
        st.dataframe(na_counts[na_counts > 0].rename("Missing").to_frame(),
                    use_container_width=True)
    else:
        st.caption("No missing values detected.")

    months = list_distinct_month_strings_from_index(time_indexed_data)
    if not months:
        st.warning("No valid months derived from the time index.")
        return
    first_month = months[0]
    st.subheader(f"First month subset: {first_month}")

    month_strings = time_indexed_data.index.to_period("M").astype(str)
    mask_first = (month_strings == first_month)
    first_month_data = time_indexed_data.loc[mask_first].copy()

    numeric_cols = list_numeric_columns(first_month_data)
    if not numeric_cols:
        st.info("No numeric columns found in the dataset.")
        return

    rows_for_display: list[dict] = []
    for col in numeric_cols:
        series = first_month_data[col].astype(float)
        rows_for_display.append(
            {
                "Variable": prettify_column_name(col),
                "Row trend": series.tolist(),        
                "Min": float(series.min()),
                "Mean": float(series.mean()),
                "Max": float(series.max()),
            }
        )

    display_df = pd.DataFrame(rows_for_display)

    display_df.columns = make_unique(list(display_df.columns))

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
