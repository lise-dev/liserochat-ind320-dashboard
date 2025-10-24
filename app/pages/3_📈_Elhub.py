import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pymongo import MongoClient

# -------------------------------------------------
# Streamlit page config
# -------------------------------------------------
st.set_page_config(
    page_title="Energy production dashboard",
    layout="wide",
)

st.title("Energy production dashboard (2021)")
st.caption(
    "Source: Elhub API → Cassandra → MongoDB Atlas (2021 hourly production data)."
)

# -------------------------------------------------
# Load data from MongoDB Atlas
# -------------------------------------------------

@st.cache_data(show_spinner=False)
def load_data_from_mongo() -> pd.DataFrame:
    """
    Connects to MongoDB Atlas using secrets, pulls the whole collection,
    and returns a cleaned pandas DataFrame ready for plotting.
    """

    # read credentials from Streamlit secrets
    uri = st.secrets["mongo"]["uri"]
    db_name = st.secrets["mongo"]["db"]
    coll_name = st.secrets["mongo"]["collection"]

    # connect and query
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    coll = client[db_name][coll_name]

    docs = list(coll.find({}, {"_id": 0}))  # drop MongoDB internal _id
    client.close()

    df = pd.DataFrame(docs)

    # parse timestamps + numeric
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce", utc=True)
    df["quantity_kwh"] = pd.to_numeric(df["quantity_kwh"], errors="coerce")

    # drop rows missing the essentials
    df = df.dropna(subset=["start_time", "quantity_kwh"])

    # helper cols
    df["year"] = df["start_time"].dt.year
    df["month"] = df["start_time"].dt.month

    return df


df_all = load_data_from_mongo()

# restrict to year 2021 only (the scope of the dashboard)
df_all = df_all[df_all["year"] == 2021].copy()

# -------------------------------------------------
# Quick preview of the raw data
# -------------------------------------------------
st.subheader("Raw data preview")
st.write(f"{len(df_all):,} rows loaded from MongoDB.")
st.dataframe(df_all.head(), use_container_width=True)

st.markdown("")

# -------------------------------------------------
# Two-column layout for the assignment
# -------------------------------------------------
left_col, right_col = st.columns(2)

# ============================
# LEFT COLUMN  → pie chart
# ============================
with left_col:
    st.markdown("#### Total production share by source")

    # radio buttons for price area
    areas = sorted(df_all["price_area"].unique().tolist())
    selected_area = st.radio(
        "Select a price area:",
        areas,
        horizontal=True,
    )

    # filter data for this area for full 2021
    df_area = df_all[df_all["price_area"] == selected_area].copy()

    # aggregate total energy by production group
    pie_df = (
        df_area
        .groupby("production_group")["quantity_kwh"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    # build pie chart
    fig_pie, ax_pie = plt.subplots(figsize=(4, 4))
    wedges, _texts = ax_pie.pie(
        pie_df["quantity_kwh"],
        startangle=90,
        wedgeprops={"linewidth": 0.5, "edgecolor": "white"},
    )
    ax_pie.set_title(f"Total production by source\n{selected_area}, 2021")

    # legend with percentages (instead of putting % on the pie)
    total_val = pie_df["quantity_kwh"].sum()
    legend_labels = []
    for group_name, val in zip(pie_df["production_group"], pie_df["quantity_kwh"]):
        pct = 100.0 * val / total_val if total_val > 0 else 0.0
        legend_labels.append(f"{group_name} — {pct:.1f}%")

    ax_pie.legend(
        wedges,
        legend_labels,
        title="production_group",
        loc="center left",
        bbox_to_anchor=(1, 0.5),
    )

    st.pyplot(fig_pie)
    plt.close(fig_pie)

# ============================
# RIGHT COLUMN → line chart
# ============================
with right_col:
    st.markdown("#### Hourly production (line chart)")

    # multiselect ~ "pills" for production group
    all_groups = sorted(df_all["production_group"].unique().tolist())
    chosen_groups = st.multiselect(
        "Select production group(s):",
        options=all_groups,
        default=all_groups,  # all selected by default
        help="These correspond to hydro / wind / solar / thermal / other.",
    )

    # month selector
    month_options = list(range(1, 13))
    chosen_month = st.selectbox(
        "Select month:",
        options=month_options,
        format_func=lambda m: f"{m:02d}",
        index=0,  # default January
    )

    # slice data for that area + month + selected groups
    df_line_src = df_all[
        (df_all["price_area"] == selected_area)
        & (df_all["month"] == chosen_month)
        & (df_all["production_group"].isin(chosen_groups))
    ].copy()

    if df_line_src.empty:
        st.info("No data for that area / month / group selection.")
    else:
        # pivot: each production_group becomes its own time series
        df_line_pivot = (
            df_line_src
            .groupby(["start_time", "production_group"])["quantity_kwh"]
            .sum()
            .reset_index()
            .pivot(
                index="start_time",
                columns="production_group",
                values="quantity_kwh",
            )
            .sort_index()
        )

        # plot with matplotlib
        fig_line, ax_line = plt.subplots(figsize=(6, 3))

        df_line_pivot.plot(ax=ax_line, linewidth=1.2)

        ax_line.set_title(
            f"Hourly production in {selected_area} ({chosen_month:02d}/2021)"
        )
        ax_line.set_ylabel("kWh")
        ax_line.set_xlabel("Time (UTC)")

        ax_line.legend(
            title="production_group",
            fontsize="small",
            ncol=2,
            loc="upper right",
        )

        st.pyplot(fig_line)
        plt.close(fig_line)

# -------------------------------------------------
# Documentation 
# -------------------------------------------------
st.markdown("---")

with st.expander("What the charts show"):
    st.markdown(
        """
        **How this page works**  
        - Left (pie): total production in 2021 for the selected price area,
          grouped by production source.  
        - Right (line): for the same area, you can pick a month and
          choose which production groups to include.  
          The chart plots hourly production in that month.
        """
    )
