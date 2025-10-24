import streamlit as st
from pathlib import Path

st.set_page_config(page_title="IND320 – Dashboard Basics", layout="wide")

def main():
    st.title("IND320 – Dashboard Basics")

    # ---------------- PROJECT INFO ----------------
    st.markdown(
        """
        **IND320 – Data to Decision**  

        ***03 October 2025:*** Part 1 – Dashboard basics **v1.1.0**  
        ***24 October 2025:*** Part 2 – Data Sources and Integration **v2.0.0**

        **About this app**
        - This project is built as part of the IND320 course.  
        - It shows how to go from raw energy data to an interactive dashboard.  
        - The app combines several tools: Python, Streamlit, and cloud databases.  
        - Part 1 focused on the basic dashboard structure and first visualizations.  
        - Part 2 extended the project with real data sources and database integration (Cassandra and MongoDB Atlas).  

        """
    )

    # CSV 
    project_root_directory = Path(__file__).resolve().parent.parent
    csv_file_path = project_root_directory / "data" / "open-meteo-subset.csv"


if __name__ == "__main__":
    main()
