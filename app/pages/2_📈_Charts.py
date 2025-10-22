import streamlit as st
from pathlib import Path
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from utils.common import (
    resolve_csv_path,
    load_time_indexed_data,
    list_distinct_month_strings_from_index,
    filter_by_month_range,
    list_numeric_columns,
    build_pretty_name_mappings,
    plot_single_series_matplotlib,
)

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(page_title="Charts", layout="wide")


def main():
    # ---------------- PAGE HEADER ----------------
    st.title("Charts")
    st.caption("Plot a single column or all numeric columns together.")

    # ---------------- DATA LOADING ----------------
    # Resolve the CSV file path from project root
    project_root = Path(__file__).resolve().parents[1]
    csv_file_path = resolve_csv_path(project_root)

    # Load data (cached for performance)
    time_indexed_data = load_time_indexed_data(csv_file_path)

    # ---------------- MONTH SELECTION ----------------
    # Extract month strings from time index for slider control
    months = list_distinct_month_strings_from_index(time_indexed_data)
    if not months:
        st.warning("No valid months found in time index.")
        return

    # Select a month range to filter the dataset
    first_month = months[0]
    start_month, end_month = st.select_slider(
        "Select month range",
        options=months,
        value=(first_month, first_month),
        help="Defaults to the first month."
    )

    # Filter the data according to selected months
    filtered_data = filter_by_month_range(time_indexed_data, start_month, end_month)

    # ---------------- COLUMN SELECTION ----------------
    # Keep only numeric columns for plotting
    numeric_cols = list_numeric_columns(filtered_data)
    if not numeric_cols:
        st.warning("No numeric columns in this month range.")
        return

    # Build pretty column name mappings for better display labels
    _, pretty_to_orig, pretty_names = build_pretty_name_mappings(numeric_cols)

    # Dropdown to select a single variable or all columns
    selected_pretty = st.selectbox(
        "Select a column (or All columns)",
        options=["All columns"] + pretty_names,
        index=0
    )

    # Display dataset info
    st.caption(
        f"Rows: {filtered_data.shape[0]:,}  |  Cols: {filtered_data.shape[1]:,}  "
        f"|  Months: {start_month} → {end_month}"
    )

    # ---------------- SINGLE COLUMN PLOT ----------------
    # If a single column is selected → display basic Matplotlib line chart
    if selected_pretty != "All columns":
        selected_original = pretty_to_orig[selected_pretty]
        fig = plot_single_series_matplotlib(filtered_data, selected_original)
        fig.axes[0].set_title(f"{selected_pretty} vs time")
        fig.axes[0].set_ylabel(selected_pretty)
        st.pyplot(fig, use_container_width=True)
        return

    # ---------------- MULTI-COLUMN PLOT (PLOTLY) ----------------
    # Option to show wind direction (°) on a separate secondary axis
    use_secondary_axis = st.checkbox(
        "Secondary axis for wind direction (°)",
        value=True,
        help="Put wind direction on the right axis so it does not dominate the other curves."
    )

    # Identify direction columns (by name) and assign axes accordingly
    direction_cols = [c for c in numeric_cols if "direction" in c.lower() or "°" in c.lower()]
    secondary_cols = direction_cols if (use_secondary_axis and direction_cols) else None
    primary_cols = [c for c in numeric_cols if not (secondary_cols and c in secondary_cols)]

    # ---------------- BUILD PLOTLY CHART ----------------
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Primary Y-axis traces (left side)
    for c in primary_cols:
        fig.add_trace(
            go.Scatter(x=filtered_data.index, y=filtered_data[c], name=c, mode="lines"),
            secondary_y=False
        )

    # Secondary Y-axis traces (right side)
    if secondary_cols:
        for c in secondary_cols:
            fig.add_trace(
                go.Scatter(
                    x=filtered_data.index,
                    y=filtered_data[c],
                    name=c,
                    mode="lines",
                    line=dict(dash="dash")
                ),
                secondary_y=True
            )

    # ---------------- LAYOUT AND STYLE ----------------
    fig.update_layout(
        title="All numeric columns (toggle in legend)",
        xaxis_title="Time",
        yaxis_title="Values (left axis)",
        yaxis2_title="Wind direction (°, right axis)",
        hovermode="x unified",
        xaxis=dict(rangeslider=dict(visible=True)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,  # places legend below plot
            xanchor="center",
            x=0.5
        )
    )

    # Display interactive Plotly chart
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
