import streamlit as st
from pathlib import Path

from utils.common import (
    resolve_csv_path,
    load_time_indexed_data,
    list_distinct_month_strings_from_index,
    filter_by_month_range,
    list_numeric_columns,
    build_pretty_name_mappings,
    plot_single_series_matplotlib,
    plot_all_series_with_optional_secondary_axis,
)

st.set_page_config(page_title="Charts", layout="wide")

def main():
    st.title("Charts")
    st.caption("Plot a single column or all numeric columns together.")

    project_root = Path(__file__).resolve().parents[1]
    csv_file_path = resolve_csv_path(project_root)
    time_indexed_data = load_time_indexed_data(csv_file_path)

    months = list_distinct_month_strings_from_index(time_indexed_data)
    if not months:
        st.warning("No valid months found in time index.")
        return

    first_month = months[0]
    start_month, end_month = st.select_slider(
        "Select month range",
        options=months,
        value=(first_month, first_month),
        help="Defaults to the first month."
    )

    filtered_data = filter_by_month_range(time_indexed_data, start_month, end_month)

    numeric_cols = list_numeric_columns(filtered_data)
    if not numeric_cols:
        st.warning("No numeric columns in this month range.")
        return
    _, pretty_to_orig, pretty_names = build_pretty_name_mappings(numeric_cols)

    selected_pretty = st.selectbox(
        "Select a column (or All columns)",
        options=["All columns"] + pretty_names,
        index=0
    )

    st.caption(
        f"Rows: {filtered_data.shape[0]:,}  |  Cols: {filtered_data.shape[1]:,}  "
        f"|  Months: {start_month} → {end_month}"
    )

    if selected_pretty != "All columns":
        selected_original = pretty_to_orig[selected_pretty]
        fig = plot_single_series_matplotlib(filtered_data, selected_original)
        fig.axes[0].set_title(f"{selected_pretty} vs time")
        fig.axes[0].set_ylabel(selected_pretty)
        st.pyplot(fig, use_container_width=True)
        return

    # Checkbox for secondary axis 
    use_secondary_axis = st.checkbox(
        "Secondary axis for wind direction (°)",
        value=True,
        help="Put wind direction on the right axis so it does not dominate the other curves."
    )

    direction_cols = [c for c in numeric_cols if "direction" in c.lower() or "°" in c.lower()]
    secondary_cols = direction_cols if (use_secondary_axis and direction_cols) else None
    primary_cols = [c for c in numeric_cols if not (secondary_cols and c in secondary_cols)]

    fig = plot_all_series_with_optional_secondary_axis(
        filtered_data,
        primary_columns=primary_cols,
        secondary_columns=secondary_cols,
        ylabel_left="Values",
        ylabel_right="Values",
    )
    st.pyplot(fig, use_container_width=True)

if __name__ == "__main__":
    main()
