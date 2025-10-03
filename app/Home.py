import streamlit as st
from pathlib import Path

st.set_page_config(page_title="IND320 – Dashboard Basics", layout="wide")

def main():
    st.title("IND320 – Dashboard Basics")
    st.markdown(
        """
        This app mirrors the notebook logic:
        - Read CSV with latin-1 encoding and comma separator
        - Parse the 'time' column, sort by time, set as the index
        - Plot single or all numeric series using Matplotlib

        Use the sidebar to navigate.
        """
    )

    # Sidebar navigation 
    with st.sidebar:
        st.page_link("app/Home.py", label="Home")
        st.page_link("app/pages/1_📊_Data.py", label="📊 Data")
        st.page_link("app/pages/2_📈_Charts.py", label="📈 Charts")
        st.page_link("app/pages/3_ℹ️_About.py", label="ℹ️ About")

    # Small hint for where the CSV is expected
    project_root_directory = Path(__file__).resolve().parent.parent
    csv_file_path = project_root_directory / "data" / "open-meteo-subset.csv"
    st.caption(f"CSV expected at: `{csv_file_path}`")

if __name__ == "__main__":
    main()
