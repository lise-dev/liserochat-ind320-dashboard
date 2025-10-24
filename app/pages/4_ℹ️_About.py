import streamlit as st

# ---------------- PAGE CONFIGURATION ----------------
st.set_page_config(page_title="About", layout="wide")


def main():
    # ---------------- PAGE HEADER ----------------
    st.title("About")
    st.caption("Lise Rochat – 2025")
    st.divider()

    # ---------------- CHANGELOG ----------------
    # Tracks the evolution of the project across parts of the assignment.
    st.markdown(
        """
        **v2.0.0**
        - Added connection to MongoDB Atlas (data integration part)
        - Created new Elhub page (Part 2) with dynamic filters and two charts  
          (pie chart + line chart)

        **v1.1.0**
        - Added month labels on time axis (Jan–Dec)
        - Reordered pages to **Data → Charts → About** for clarity
        - Added dataset overview (`describe()`, distinct months, shape)
        - Switched "all columns" chart to **Plotly** (legend toggle + range slider)
        - Improved legend placement and axis labels
        - Added concise English comments across pages

        **v1.0.0**
        - Initial multipage Streamlit app
        - Created utilities module for data loading and visualization
        - Added first-month sparkline table
        - Implemented first Matplotlib charts
        """
    )

    # ---------------- SIDEBAR ----------------
    with st.sidebar:
        st.header("About")
        st.write("Project roadmap (Part 1 of 4)")


if __name__ == "__main__":
    main()
