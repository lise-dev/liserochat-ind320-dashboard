import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(page_title="About", layout="wide")


def main():
    # ---------------- PAGE HEADER ----------------
    st.title("About")
    st.caption("Lise Rochat – 2025")
    st.divider()

    # ---------------- PROJECT INFO ----------------
    # Show current version and context.
    st.markdown(
        """
        **IND320 – Data to Decision**  
        ***03 October 2025:*** Part 1 – Dashboard basics **v1.1.0**

        **What this app includes**
        - Multipage layout scaffold
        - Sidebar-ready controls
        - Shared utilities module (`utils/common.py`)
        - Data page with descriptive statistics and first-month sparklines
        - Charts page with single-series (Matplotlib) and all-series (Plotly) views
        """
    )

    # ---------------- CHANGELOG ----------------
    # Changelog for transparency and to document iteration across submissions.
    with st.expander("Changelog"):
        st.markdown(
            """
            **v1.1.0**
            - Show explicit month labels on time axis (Jan–Dec)
            - Reordered pages to **Data → Charts → About** for clarity
            - Added dataset overview: `describe()`, coverage, distinct months, shape
            - Switched "all columns" chart to **Plotly** (legend toggle + range slider)
            - Improved legend placement and axis labelling for readability
            - Added concise English code comments across pages

            **v1.0.0**
            - Initial multipage Streamlit app
            - Utilities module for loading/transforming/plotting
            - First-month sparkline table
            - Basic Matplotlib charts
            """
        )

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.header("About")
        st.write("Project roadmap (Part 1 of 4)")

if __name__ == "__main__":
    main()
